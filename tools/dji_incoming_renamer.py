#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "wordninja==2.0.0",
# ]
# ///
"""Re-home DJI captures into the TIM naming pattern, with a journal-based undo.

Incoming pattern (as dropped off by the pilot)::

    W:\\Incoming\\Drones\\ELC\\2026-Aug\\DCIM\\DJI_202608051635_001_01ClearCreek1\\DJI_*.JPG
    W:\\Incoming\\Drones\\ELC\\2026-Aug\\MISC\\...

Outgoing pattern (the processing queue)::

    W:\\Incoming\\Drones\\TIM\\2026-08-10-2b-Dominion-Remap\\DCIM\\DJI_202608101454_011_2bdominionremap\\DJI_*.JPG

Every file gets a destination of ``<dest>/<YYYY-MM-DD>-<Project-Name>/<relative
path from source root>``.  The date comes from the flight folder name, the file
name, the nearest dated ancestor folder, or (last resort) the file mtime.  The
project label is the pilot's own flight name with DJI's
``<brand>_<YYYYMMDDHHMM>_<flight index>_`` prefix removed, then un-squished into
words (``--style split``, the default):

    DJI_202608101454_011_2bdominionremap  ->  .../TIM/2026-08-10-2b-Dominion-Remap/DCIM/...
    DJI_202608051635_001_01ClearCreek1    ->  .../TIM/2026-08-05-01-Clear-Creek-1/DCIM/...

Word splitting learns from the archive itself: existing ``TIM/<date>-<label>``
folders contribute the place names and mission words in use, so ``Pondy-Pit``
splits although "pondy" is not an English word, while ``Mendenhall`` is left
alone because the archive already spells it that way.  A label that is already
archived keeps the archive's exact spelling, so re-imports cannot sprout a
second, differently-hyphenated folder (``--restyle`` ignores that and renames
anyway).  ``--style camel`` splits only on camelCase, ``--style verbatim`` keeps
the pilot's text untouched (apart from path-illegal characters), and
``--project`` overrides every label.
Everything a run does is written to a JSON journal so ``undo`` can put it back.

This tool moves whole capture folders and names the dated folder; it does not
rewrite individual file names.

Usage
-----
    uv run tools/dji_incoming_renamer.py adapt "W:\\Incoming\\Drones\\ELC\\2026-Aug"
    uv run tools/dji_incoming_renamer.py adapt "...\\2026-Aug" --apply
    uv run tools/dji_incoming_renamer.py adapt ... --project "Cowley Creek" --apply
    uv run tools/dji_incoming_renamer.py adapt ... --only-date 2026-08-09 --apply
    uv run tools/dji_incoming_renamer.py runs
    uv run tools/dji_incoming_renamer.py undo --last            # preview
    uv run tools/dji_incoming_renamer.py undo --last --apply    # restore

``adapt`` is a dry run unless ``--apply`` is passed.  ``undo`` likewise previews
until ``--apply``.

Installed as a command with ``uvs install tools/dji_incoming_renamer.py`` (tool
name ``dji-incoming-renamer``); re-run ``uvs update tools/dji_incoming_renamer.py``
after edits.
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import json
import os
import re
import shutil
import sys
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

try:  # pinned in the PEP 723 block; degrade if absent
    import wordninja as _wordninja
    from wordninja import DEFAULT_LANGUAGE_MODEL as _WORD_MODEL
except Exception:  # pragma: no cover - dependency missing or renamed
    _wordninja = None  # type: ignore[assignment]
    _WORD_MODEL = None  # type: ignore[assignment]

DEFAULT_DEST = Path(r"W:\Incoming\Drones\TIM")
DEST_ENV = "DJI_TIM_ROOT"
JOURNAL_ENV = "DJI_INCOMING_RENAMER_JOURNAL"
TOOL_NAME = "dji-incoming-renamer"
JOURNAL_VERSION = 1

#: Directory names that are plumbing, not project labels.
CONTAINER_NAMES = {
    "DCIM",
    "MISC",
    "SD-01",
    "SD-02",
    "SD-03",
    "SD-04",
    "PRIVATE",
    "AVCHD",
    "PANORAMA",
    "100MEDIA",
    "101MEDIA",
    "102MEDIA",
    "TEMP",
}

#: Directory names never descended into (unless MISC is requested).
SKIP_DIR_NAMES = {
    "LOST.DIR",
    "$RECYCLE.BIN",
    "SYSTEM VOLUME INFORMATION",
    "__PYCACHE__",
}

_DATE_RE = re.compile(r"((?:19|20)\d{2})[-_.]?(\d{2})[-_.]?(\d{2})")
_CAMERA_PREFIX_RE = re.compile(
    r"^(?:DJI|PXL|GOPR|GP|IMG|VID|MVI|DSC|DJIFLY)[-_\s]*", re.IGNORECASE
)
#: DJI's own prefix: <brand>_<YYYYMMDDHHMM>_<flight index>_<pilot label>
_FLIGHT_PREFIX_RE = re.compile(
    r"^(?:DJI|PXL|GOPR|GP|IMG|VID|MVI|DSC|DJIFLY)[-_\s]*"
    r"(?:\d{8,14}(?:[-_\s]+\d{1,4})?[-_\s]+)?",
    re.IGNORECASE,
)
_LEADING_UNIT_RE = re.compile(r"^\d{1,3}[a-z]{0,1}(?=[A-Za-z]{3,})")
_CAMEL_RE = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_DIGIT_SPLIT_RE = re.compile(r"(?<=[A-Za-z]{3})(?=\d)")
_WORD_SPLIT_RE = re.compile(r"[^\w']+", re.UNICODE)
_ILLEGAL_PATH_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

#: Short tokens worth splitting out although they are not dictionary words.
_SHORT_TOKENS = {
    "rd",
    "st",
    "ave",
    "ln",
    "ct",
    "dr",
    "hwy",
    "mt",
    "ft",
    "pk",
    "cr",
    "ck",
    "lk",
    "pt",
    "jr",
    "sr",
    "us",
    "bc",
    "yt",
    "ak",
    "nwt",
    "nw",
    "ne",
    "sw",
    "se",
}

_NAME_PREFIXES = {"mc", "mac", "van", "von", "de", "la", "le", "du"}

#: Shortest English word we will find inside a squished run.
_MIN_PIECE = 4

#: Cost for words only the archive knows about (lower = preferred).
_DOMAIN_COST = 8.0

#: Longest label we will write; keeps whole paths well inside MAX_PATH.
_MAX_LABEL = 96


def sanitize_label(text: str) -> str:
    """Keep a label as typed; only make it path-legal."""
    text = _ILLEGAL_PATH_RE.sub("-", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"-{2,}", "-", text)
    return text.strip(" .-")


def normalize_label(text: str) -> str:
    """Letters and digits only, lowercased: how two labels are compared."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def cap_label(slug: str, limit: int = _MAX_LABEL) -> str:
    """Trim at a word boundary so one silly label cannot blow out MAX_PATH."""
    if len(slug) <= limit:
        return slug
    cut = slug.rfind("-", 0, limit)
    return (slug[:cut] if cut > 0 else slug[:limit]).strip("-.")


@dataclass
class Lexicon:
    """Word knowledge for splitting squished flight names.

    Three sources, in order of trust:

    * ``spellings`` - every label already archived, so a re-import keeps the
      exact folder name it had before (cross-referencing must not drift).
    * ``names`` - archive labels that are a single word (``Mendenhall``), kept
      whole rather than split into ``Men-Den-Hall``.
    * ``domain`` - words taken from existing ``TIM/<date>-<label>`` folders, so
      ``pondypit`` splits as ``Pondy-Pit`` even though "pondy" is not English.
    * ``english`` - frequencies from ``wordninja``, the general fallback.
    """

    english: dict[str, float] = field(default_factory=dict)
    domain: set[str] = field(default_factory=set)
    names: set[str] = field(default_factory=set)
    spellings: dict[str, str] = field(default_factory=dict)
    cache: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_archive(cls, dest_root: Path) -> Lexicon:
        english = dict(_WORD_MODEL._wordcost) if _WORD_MODEL else {}  # noqa: SLF001
        lexicon = cls(english=english)
        try:
            children = sorted(dest_root.iterdir())
        except OSError:
            return lexicon
        for child in children:
            match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", child.name)
            if not match or not child.is_dir():
                continue
            label = match.group(1)
            normalized = normalize_label(label)
            lexicon.spellings.setdefault(normalized, label)
            if _WORD_SPLIT_RE.search(label) is None:
                lexicon.names.add(normalized)
            for part in re.split(r"[^A-Za-z0-9]+", label):
                for word in _CAMEL_RE.split(part):  # CopperHaul -> copper, haul
                    if len(word) >= 2 and not word.isdigit():
                        lexicon.domain.add(word.lower())
        return lexicon

    def segment(self, token: str) -> list[str]:
        """``dominionremap`` -> ``["dominion", "remap"]``; leave unknowns alone."""
        if token not in self.cache:
            self.cache[token] = self._best(token)
        return self.cache[token]

    def _best(self, token: str) -> list[str]:
        if len(token) < 2 * _MIN_PIECE:
            return [token]
        # Trust real words first, then the archive's own spelling, then the
        # frequency-list fallback: "cowleycreek" splits even though the archive
        # has "Cowley-Creek", while "mendenhall" stays whole.
        strict = self._strict(token)
        if strict:
            return strict
        if token.lower() in self.names:
            return [token]
        return self._loose(token) or [token]

    def _piece_cost(self, piece: str) -> float | None:
        low = piece.lower()
        if len(piece) >= _MIN_PIECE and low in self.english:
            return self.english[low]
        if low in self.domain:
            return _DOMAIN_COST
        if low in _SHORT_TOKENS:
            return _DOMAIN_COST + 2.0
        return None

    def _strict(self, token: str) -> list[str] | None:
        """Best split where every piece is a word we actually trust."""
        low = token.lower()
        size = len(low)
        best = [float("inf")] * (size + 1)
        back = [-1] * (size + 1)
        best[0] = 0.0
        for end in range(1, size + 1):
            for start in range(max(0, end - 32), end):
                if best[start] == float("inf"):
                    continue
                cost = self._piece_cost(low[start:end])
                if cost is None:
                    continue
                if best[start] + cost < best[end]:
                    best[end] = best[start] + cost
                    back[end] = start
        if best[-1] == float("inf") or back[-1] <= 0:
            return None
        return self._walk(token, back)

    def _loose(self, token: str) -> list[str] | None:
        """Fall back to wordninja, then glue its short fragments back together.

        Catches words the frequency list lacks, e.g. ``dominionremap`` ->
        ``dominion | re | map`` -> ``Dominion-Remap``.
        """
        if _wordninja is None:
            return None
        pieces = _wordninja.split(token)
        if len(pieces) < 2:
            return None
        glued: list[str] = []
        carry = ""
        for piece in pieces:
            piece = carry + piece
            carry = ""
            if len(piece) < _MIN_PIECE:
                carry = piece
                continue
            glued.append(piece)
        if carry:
            if not glued:
                return None
            glued[-1] += carry
        if not 2 <= len(glued) <= 4 or any(len(p) < 3 for p in glued):
            return None
        if token.islower() or token.isupper():
            glued = [p[:1].upper() + p[1:].lower() for p in glued]
        return glued

    @staticmethod
    def _walk(token: str, back: list[int]) -> list[str]:
        parts: list[str] = []
        end = len(token)
        while end > 0:
            start = back[end]
            parts.append(token[start:end])
            end = start
        parts.reverse()
        return parts


def label_tokens(label: str) -> list[str]:
    """Break a flight label into raw tokens: app index, words, numbers."""
    text = _ILLEGAL_PATH_RE.sub(" ", label)
    prefix = ""
    match = _LEADING_UNIT_RE.match(text)
    if match:
        prefix, text = match.group(0), text[match.end() :]
    text = _CAMEL_RE.sub("-", text)
    text = _DIGIT_SPLIT_RE.sub("-", text)
    tokens = [t.strip("'.") for t in _WORD_SPLIT_RE.split(text)]
    tokens = [t for t in tokens if t]
    if prefix:
        tokens.insert(0, prefix)
    merged: list[str] = []
    for token in tokens:  # keep Mc/Mac/O' names in one piece
        if merged and merged[-1].lower() in _NAME_PREFIXES and token[:1].isupper():
            merged[-1] += token
        else:
            merged.append(token)
    return merged


def format_label(label: str, *, style: str, lexicon: Lexicon) -> str | None:
    """Render a flight label in *style*; None when nothing usable is left."""
    if style == "verbatim":
        return cap_label(sanitize_label(label)) or None
    out: list[str] = []
    for token in label_tokens(label):
        if style == "split" and token.isalpha():
            out.extend(lexicon.segment(token))
        else:
            out.append(token)
    words = []
    for token in out:
        if not token:
            continue
        if token.isupper() and len(token) <= 5:
            words.append(token)  # keep acronyms (CH, DJI, USGS)
        else:
            words.append(token[0].upper() + token[1:])
    return cap_label("-".join(words)) or None


def extract_date(text: str) -> date | None:
    """First plausible YYYYMMDD / YYYY-MM-DD / YYYY_MM_DD in *text*."""
    for match in _DATE_RE.finditer(text):
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue
    return None


def project_from_name(
    name: str, *, style: str = "split", lexicon: Lexicon | None = None
) -> str | None:
    """Project label from a flight folder, minus DJI's own prefix.

    ``DJI_202608101454_011_2bdominionremap`` -> ``2b-Dominion-Remap``.
    """
    text = name.strip()
    if not text or text.upper() in CONTAINER_NAMES:
        return None
    label = _FLIGHT_PREFIX_RE.sub("", text).strip()
    if not label:
        return None
    lexicon = lexicon or Lexicon()
    if style != "verbatim":
        # Re-use the archive's own spelling so a re-import of an already-known
        # mission cannot sprout a second, differently-hyphenated folder.
        archived = lexicon.spellings.get(normalize_label(label))
        if archived:
            return archived
    return format_label(label, style=style, lexicon=lexicon)


def human_size(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------


@dataclass
class Entry:
    """One file that wants a new home."""

    src: Path
    rel_parent: Path  # containing dir, relative to the scan root
    when: date
    project: str
    size: int
    mtime: float
    misc: bool = False
    mtime_dated: bool = False  # no date in any name; guessed from mtime


@dataclass
class PlanItem:
    entry: Entry
    group: str
    dst: Path
    replaces: bool = False


@dataclass
class Plan:
    src_root: Path
    dest_root: Path
    items: list[PlanItem] = field(default_factory=list)
    skipped: list[tuple[Entry, str]] = field(default_factory=list)

    @property
    def groups(self) -> dict[str, list[PlanItem]]:
        grouped: dict[str, list[PlanItem]] = {}
        for item in self.items:
            grouped.setdefault(item.group, []).append(item)
        return dict(sorted(grouped.items()))

    @property
    def replaced(self) -> int:
        return sum(1 for item in self.items if item.replaces)

    @property
    def mtime_dated(self) -> int:
        return sum(1 for item in self.items if item.entry.mtime_dated)


def resolve_scan_root(src: Path) -> Path:
    """Pointing at .../DCIM should still produce DCIM/... below the dated folder."""
    if src.name.upper() in {"DCIM", "MISC"} and src.parent != src:
        return src.parent
    return src


def _skip_dir(name: str, include_misc: bool) -> bool:
    upper = name.upper()
    if upper.startswith("$") or upper in SKIP_DIR_NAMES:
        return True
    return upper == "MISC" and not include_misc


def _is_excluded(rel: Path, patterns: list[str]) -> bool:
    if not patterns:
        return False
    rel_posix = rel.as_posix()
    return any(
        fnmatch.fnmatch(rel.name, pat) or fnmatch.fnmatch(rel_posix, pat)
        for pat in patterns
    )


def _date_with_source(path: Path, root: Path) -> tuple[date, str] | None:
    """Date from the containing folder, any dated ancestor, or the file name."""
    current = path.parent
    while True:
        found = extract_date(current.name)
        if found:
            return found, "folder"
        if current == root or current.parent == current:
            break
        current = current.parent
    found = extract_date(path.name)
    if found:
        return found, "filename"
    return None


def iter_entries(
    root: Path,
    *,
    include_misc: bool,
    excludes: list[str],
    style: str = "split",
    lexicon: Lexicon | None = None,
) -> list[Entry]:
    entries: list[Entry] = []
    labels: dict[str, str] = {}  # folder name -> label, so 8k files do 9 lookups
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not _skip_dir(d, include_misc))
        here = Path(dirpath)
        for name in sorted(filenames):
            path = here / name
            if name.startswith("."):
                continue
            try:
                rel = path.relative_to(root)
            except ValueError:  # pragma: no cover - defensive
                continue
            if _is_excluded(rel, excludes):
                continue
            is_misc = any(part.upper() == "MISC" for part in rel.parts[:-1])
            if here.name not in labels:
                labels[here.name] = (
                    project_from_name(here.name, style=style, lexicon=lexicon)
                    or "Unknown"
                )
            project = labels[here.name]
            dated = _date_with_source(path, root)
            try:
                stat = path.stat()
            except OSError:
                continue
            if dated is None:
                entries.append(
                    Entry(
                        src=path,
                        rel_parent=here.relative_to(root),
                        when=datetime.fromtimestamp(stat.st_mtime).date(),
                        project=project,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        misc=is_misc,
                        mtime_dated=True,
                    )
                )
                continue
            when, _source = dated
            entries.append(
                Entry(
                    src=path,
                    rel_parent=here.relative_to(root),
                    when=when,
                    project=project,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    misc=is_misc,
                )
            )
    return entries


def _unique_path(dst: Path, claimed: set[Path]) -> Path:
    stem, suffix = dst.stem, dst.suffix
    index = 1
    while True:
        candidate = dst.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists() and candidate not in claimed:
            return candidate
        index += 1


def build_plan(
    src_root: Path,
    dest_root: Path,
    *,
    project_override: str | None = None,
    style: str = "split",
    lexicon: Lexicon | None = None,
    date_override: date | None = None,
    only_dates: set[date] | None = None,
    include_misc: bool = False,
    excludes: list[str] | None = None,
    on_conflict: str = "skip",
) -> Plan:
    plan = Plan(src_root=src_root, dest_root=dest_root)
    entries = iter_entries(
        src_root,
        include_misc=include_misc,
        excludes=excludes or [],
        style=style,
        lexicon=lexicon,
    )

    wanted: list[tuple[Entry, str]] = []
    for entry in entries:
        if entry.misc:
            continue
        when = date_override or entry.when
        if only_dates and when not in only_dates:
            plan.skipped.append((entry, f"date {when.isoformat()} not selected"))
            continue
        project = project_override or entry.project
        wanted.append((entry, f"{when.isoformat()}-{project}"))

    # MISC (thumbnails, DJI db) belongs to the card, not to a date: park it in
    # the earliest destination group rather than inventing <date>-THM groups.
    misc_entries = [e for e in entries if e.misc]
    if misc_entries:
        if only_dates:
            keep = []
            for entry in misc_entries:
                when = date_override or entry.when
                if when in only_dates:
                    keep.append(entry)
                else:
                    plan.skipped.append(
                        (entry, f"date {when.isoformat()} not selected")
                    )
            misc_entries = keep
        if misc_entries:
            target = min((group for _entry, group in wanted), default=None)
            if target is None:
                when = date_override or min(e.when for e in misc_entries)
                target = f"{when.isoformat()}-{project_override or 'Unknown'}"
            wanted.extend((entry, target) for entry in misc_entries)

    claimed: set[Path] = set()
    for entry, group in wanted:
        dst = dest_root / group / entry.rel_parent / entry.src.name
        if dst == entry.src:
            plan.skipped.append((entry, "already in place"))
            continue
        replaces = False
        if dst.is_dir():
            # shutil.move would quietly bury the file inside that folder.
            if on_conflict == "rename":
                dst = _unique_path(dst, claimed)
            else:
                plan.skipped.append((entry, "a folder already occupies the target"))
                continue
        elif dst.exists() or dst in claimed:
            if on_conflict == "rename":
                dst = _unique_path(dst, claimed)
            elif on_conflict == "skip":
                plan.skipped.append((entry, "destination already exists"))
                continue
            else:
                replaces = True
        claimed.add(dst)
        plan.items.append(
            PlanItem(entry=entry, group=group, dst=dst, replaces=replaces)
        )
    return plan


# --------------------------------------------------------------------------
# journal
# --------------------------------------------------------------------------


def default_journal_dir() -> Path:
    env = os.environ.get(JOURNAL_ENV)
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(base) / TOOL_NAME / "journal"
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / TOOL_NAME / "journal"


@dataclass
class Journal:
    id: str
    created: str
    status: str
    op: str  # move | copy
    src_root: str
    dest_root: str
    options: dict
    ops: list[dict]
    created_dirs: list[str] = field(default_factory=list)
    pruned_dirs: list[str] = field(default_factory=list)
    path: Path | None = None
    version: int = JOURNAL_VERSION

    @classmethod
    def new(cls, plan: Plan, op: str, options: dict) -> Journal:
        stamp = datetime.now(timezone.utc)
        return cls(
            id=stamp.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6],
            created=stamp.isoformat(timespec="seconds"),
            status="pending",
            op=op,
            src_root=str(plan.src_root),
            dest_root=str(plan.dest_root),
            options=options,
            ops=[
                {
                    "src": str(i.entry.src),
                    "dst": str(i.dst),
                    "group": i.group,
                    "size": i.entry.size,
                    "mtime": i.entry.mtime,
                    "replaces": i.replaces,
                }
                for i in plan.items
            ],
        )

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "id": self.id,
            "created": self.created,
            "status": self.status,
            "op": self.op,
            "src_root": self.src_root,
            "dest_root": self.dest_root,
            "options": self.options,
            "created_dirs": self.created_dirs,
            "pruned_dirs": self.pruned_dirs,
            "ops": self.ops,
        }

    @classmethod
    def from_dict(cls, data: dict, path: Path) -> Journal:
        return cls(
            id=data["id"],
            created=data.get("created", ""),
            status=data.get("status", "unknown"),
            op=data.get("op", "move"),
            src_root=data.get("src_root", ""),
            dest_root=data.get("dest_root", ""),
            options=data.get("options", {}),
            ops=data.get("ops", []),
            created_dirs=data.get("created_dirs", []),
            pruned_dirs=data.get("pruned_dirs", []),
            path=path,
            version=data.get("version", JOURNAL_VERSION),
        )

    def write(self, journal_dir: Path) -> Path:
        journal_dir.mkdir(parents=True, exist_ok=True)
        target = self.path or (journal_dir / f"{self.id}.json")
        tmp = target.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, target)
        self.path = target
        return target


def load_journals(journal_dir: Path) -> list[Journal]:
    if not journal_dir.is_dir():
        return []
    runs = []
    for path in sorted(journal_dir.glob("*.json"), reverse=True):
        try:
            runs.append(Journal.from_dict(json.loads(path.read_text("utf-8")), path))
        except (OSError, ValueError, KeyError) as exc:
            print(f"warning: unreadable journal {path}: {exc}", file=sys.stderr)
    runs.sort(key=lambda j: j.created, reverse=True)
    return runs


def find_run(journal_dir: Path, selector: str) -> Journal | None:
    runs = load_journals(journal_dir)
    exact = [j for j in runs if j.id == selector]
    if exact:
        return exact[0]
    prefixed = [j for j in runs if j.id.startswith(selector)]
    return prefixed[0] if len(prefixed) == 1 else None


# --------------------------------------------------------------------------
# apply / undo
# --------------------------------------------------------------------------


def _ensure_dir(path: Path, created: list[Path], stop: Path) -> None:
    """mkdir -p, recording the directories that did not exist (below *stop*)."""
    missing = []
    current = path
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir()
        if directory != stop and stop in directory.parents:
            created.append(directory)


class LockError(RuntimeError):
    """Another run already holds the journal lock."""


@contextlib.contextmanager
def run_lock(journal_dir: Path):
    """Stop two runs from interleaving moves against the same journal dir."""
    journal_dir.mkdir(parents=True, exist_ok=True)
    lock = journal_dir / ".lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        holder = ""
        try:
            holder = lock.read_text("utf-8").strip()
        except OSError:
            pass
        raise LockError(
            f"another run holds {lock} ({holder or 'owner unknown'}); "
            "wait for it to finish, or delete the file if it is stale"
        ) from exc
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(
            f"pid {os.getpid()} since {datetime.now().isoformat(timespec='seconds')}"
        )
    try:
        yield
    finally:
        try:
            lock.unlink()
        except OSError:
            pass


def apply_plan(
    plan: Plan,
    journal_dir: Path,
    *,
    op: str,
    overwrite: bool,
    prune: bool = True,
    prune_root: bool = False,
) -> Journal:
    journal = Journal.new(
        plan,
        op,
        {
            "copy": op == "copy",
            "overwrite": overwrite,
            "prune": prune,
            "prune_root": prune_root,
        },
    )
    journal.path = journal.write(journal_dir)
    created: list[Path] = []
    for item, record in zip(plan.items, journal.ops, strict=True):
        dst = item.dst
        _ensure_dir(dst.parent, created, plan.dest_root)
        if item.replaces and dst.is_file():
            # Park the old file beside the new one so undo can bring it back.
            backup = dst.with_name(f"{dst.name}.replaced-{journal.id}")
            os.replace(dst, backup)
            record["backup"] = str(backup)
        if op == "copy":
            shutil.copy2(item.entry.src, dst)
        else:
            shutil.move(str(item.entry.src), str(dst))
    journal.created_dirs = [str(p) for p in created]
    if prune:
        journal.pruned_dirs = [
            str(p)
            for p in prune_empty_dirs(
                plan.src_root,
                [i.entry.src for i in plan.items],
                include_root=prune_root,
            )
        ]
    journal.status = "applied"
    missing = []
    for item in plan.items:
        try:
            arrived = item.dst.is_file() and (
                op == "move" or item.dst.stat().st_size == item.entry.size
            )
        except OSError:
            arrived = False
        if not arrived:
            missing.append(str(item.dst))
    if missing:
        journal.status = "incomplete"
        print(
            f"warning: {len(missing)} file(s) did not arrive intact "
            f"(first: {missing[0]})",
            file=sys.stderr,
        )
    journal.write(journal_dir)
    return journal


def prune_empty_dirs(
    root: Path, moved_from: list[Path], *, include_root: bool
) -> list[Path]:
    """Remove folders emptied by *moved_from*, never unrelated empty folders.

    The scan root is the pilot's drop-off folder, so it only goes away when
    *include_root* is set.
    """
    pruned: list[Path] = []
    if not root.is_dir():
        return pruned
    candidates: set[Path] = set()
    for path in moved_from:
        parent = path.parent
        while root == parent or root in parent.parents:
            if parent != root or include_root:
                candidates.add(parent)
            if parent == root:
                break
            parent = parent.parent
    for directory in sorted(candidates, key=lambda p: len(p.parts), reverse=True):
        try:
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
                pruned.append(directory)
        except OSError:
            continue
    return pruned


@dataclass
class UndoAction:
    op: str  # restore | delete | skip
    src: Path | None
    dst: Path | None
    note: str = ""
    backup: Path | None = None


def _changed_since_run(path: Path, raw: dict) -> str | None:
    """Describe how *path* differs from what the journal recorded, if it does."""
    try:
        stat = path.stat()
    except OSError:
        return "unreadable"
    size = raw.get("size")
    if isinstance(size, int) and size != stat.st_size:
        return f"size changed ({size} -> {stat.st_size})"
    mtime = raw.get("mtime")
    if isinstance(mtime, (int, float)) and abs(mtime - stat.st_mtime) > 2:
        return "modified after the run"
    return None


def plan_undo(journal: Journal) -> list[UndoAction]:
    actions: list[UndoAction] = []
    for raw in reversed(journal.ops):
        src = Path(raw["src"])
        dst = Path(raw["dst"])
        backup = Path(raw["backup"]) if raw.get("backup") else None
        if journal.op == "copy":
            if not dst.exists():
                actions.append(UndoAction("skip", None, dst, "already gone", backup))
                continue
            changed = _changed_since_run(dst, raw)
            if changed:
                actions.append(
                    UndoAction("skip", None, dst, f"copy {changed}; left alone", backup)
                )
            else:
                actions.append(
                    UndoAction("delete", None, dst, "remove copied file", backup)
                )
            continue
        if dst.exists() and not src.exists():
            changed = _changed_since_run(dst, raw)
            note = "move back" if changed is None else f"move back ({changed})"
            actions.append(UndoAction("restore", src, dst, note, backup))
        elif not dst.exists():
            actions.append(UndoAction("skip", src, dst, "destination missing"))
        else:
            actions.append(UndoAction("skip", src, dst, "source already exists"))
    return actions


def apply_undo(journal: Journal, actions: list[UndoAction], journal_dir: Path) -> int:
    restored = 0
    for action in actions:
        if action.op == "restore" and action.src and action.dst:
            action.src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(action.dst), str(action.src))
            if action.backup and action.backup.exists():
                shutil.move(str(action.backup), str(action.dst))
            restored += 1
        elif action.op == "delete" and action.dst:
            action.dst.unlink()
            if action.backup and action.backup.exists():
                shutil.move(str(action.backup), str(action.dst))
            restored += 1
    for raw in sorted(journal.created_dirs, key=len, reverse=True):
        directory = Path(raw)
        try:
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        except OSError:
            continue
    for raw in sorted(journal.pruned_dirs, key=len):
        Path(raw).mkdir(parents=True, exist_ok=True)
    journal.status = "undone"
    journal.options = {
        **journal.options,
        "undone_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    journal.write(journal_dir)
    return restored


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def render_plan(plan: Plan) -> None:
    groups = plan.groups
    total_files = len(plan.items)
    total_bytes = sum(i.entry.size for i in plan.items)
    print(f"Source : {plan.src_root}")
    print(f"Dest   : {plan.dest_root}")
    print(
        f"Files  : {total_files:,} ({human_size(total_bytes)}) in {len(groups)} group(s)"
    )
    if plan.mtime_dated:
        print(
            f"WARNING: {plan.mtime_dated:,} file(s) had no date in any name; "
            "dated from file mtime"
        )
    if plan.replaced:
        print(
            f"NOTE: {plan.replaced:,} existing destination file(s) will be "
            "replaced and kept as .replaced-<run> backups for undo"
        )
    print()
    width = min(48, max((len(g) for g in groups), default=10))
    for group, items in groups.items():
        size = sum(i.entry.size for i in items)
        subdirs = {i.entry.rel_parent.as_posix() for i in items}
        sample = sorted(subdirs)[0] if subdirs else "."
        if len(subdirs) > 1:
            sample += f" (+{len(subdirs) - 1} more)"
        print(
            f"  {group:<{width}}  {len(items):>5} files  {human_size(size):>9}  {sample}"
        )
    if plan.skipped:
        print()
        print(f"Skipped: {len(plan.skipped):,} file(s)")
        reasons: dict[str, int] = {}
        for _entry, reason in plan.skipped:
            key = reason.split(":")[0]
            reasons[key] = reasons.get(key, 0) + 1
        for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1])[:6]:
            print(f"  {count:>5}  {reason}")
        for entry, reason in plan.skipped[:5]:
            print(f"    - {entry.src} ({reason})")


def render_runs(runs: list[Journal]) -> None:
    if not runs:
        print("no journaled runs")
        return
    print(f"{'ID':<26} {'CREATED':<20} {'STATUS':<9} {'OP':<5} {'FILES':>6}  SOURCE")
    for run in runs:
        print(
            f"{run.id:<26} {run.created:<20} {run.status:<9} {run.op:<5} "
            f"{len(run.ops):>6}  {run.src_root}"
        )


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def parse_iso_date(text: str) -> date:
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {text!r}") from exc


def cmd_adapt(args: argparse.Namespace) -> int:
    src = Path(args.src).expanduser()
    if not src.is_dir():
        print(f"error: source folder not found: {src}", file=sys.stderr)
        return 2
    src = resolve_scan_root(src.resolve())
    dest_root = Path(args.dest or os.environ.get(DEST_ENV) or DEFAULT_DEST).expanduser()
    if not dest_root.is_absolute():
        dest_root = Path.cwd() / dest_root
    try:  # compare real paths, but keep the given form for display
        dest_real = dest_root.resolve()
    except OSError:
        dest_real = dest_root
    if dest_real == src or src in dest_real.parents or dest_real in src.parents:
        print(
            "error: source and destination must not contain each other",
            file=sys.stderr,
        )
        return 2
    lexicon = Lexicon.from_archive(dest_root)
    if args.restyle:
        lexicon.spellings.clear()  # ignore how TIM already spells these labels
    if args.project:
        project = format_label(args.project, style=args.style, lexicon=lexicon)
        if not project:
            print("error: --project is empty after sanitising", file=sys.stderr)
            return 2
    else:
        project = None
    plan = build_plan(
        src,
        dest_root,
        project_override=project,
        style=args.style,
        lexicon=lexicon,
        date_override=args.date,
        only_dates=set(args.only_date or []),
        include_misc=args.include_misc,
        excludes=args.exclude or [],
        on_conflict=args.on_conflict,
    )
    render_plan(plan)
    if not plan.items:
        print("\nNothing to do.")
        return 0
    if not args.apply or args.dry_run:
        print("\nDry run - no changes made. Re-run with --apply to execute.")
        return 0
    op = "copy" if args.copy else "move"
    journal_dir = (
        Path(args.journal_dir).expanduser()
        if args.journal_dir
        else default_journal_dir()
    )
    with run_lock(journal_dir):
        journal = apply_plan(
            plan,
            journal_dir,
            op=op,
            overwrite=args.on_conflict == "overwrite",
            prune=not args.keep_empty,
            prune_root=args.prune_root,
        )
    print(f"\n{'Copied' if op == 'copy' else 'Moved'} {len(plan.items):,} file(s).")
    print(f"Journal: {journal.path}")
    if journal.pruned_dirs:
        print(f"Pruned {len(journal.pruned_dirs)} empty source folder(s).")
    print(f"Undo with: {TOOL_NAME} undo --run {journal.id} --apply")
    return 0


def cmd_runs(args: argparse.Namespace) -> int:
    journal_dir = (
        Path(args.journal_dir).expanduser()
        if args.journal_dir
        else default_journal_dir()
    )
    runs = load_journals(journal_dir)
    if args.json:
        print(json.dumps([r.to_dict() for r in runs], indent=2, ensure_ascii=False))
        return 0
    print(f"Journal: {journal_dir}\n")
    render_runs(runs[: args.limit])
    return 0


def cmd_undo(args: argparse.Namespace) -> int:
    journal_dir = (
        Path(args.journal_dir).expanduser()
        if args.journal_dir
        else default_journal_dir()
    )
    runs = load_journals(journal_dir)
    if args.list:
        print(f"Journal: {journal_dir}\n")
        render_runs(runs)
        return 0
    if args.run:
        journal = find_run(journal_dir, args.run)
        if journal is None:
            print(f"error: no unique run matching {args.run!r}", file=sys.stderr)
            return 2
    else:
        pending = [r for r in runs if r.status in {"applied", "incomplete"}]
        if not pending and args.force:
            pending = [r for r in runs if r.status == "undone"]
        if not pending:
            print("error: no applied run to undo", file=sys.stderr)
            return 2
        journal = pending[0]
    if journal.status == "undone" and not args.force:
        print(
            f"error: run {journal.id} was already undone "
            "(use --force to repeat the reversal)",
            file=sys.stderr,
        )
        return 2

    actions = plan_undo(journal)
    restorable = [a for a in actions if a.op != "skip"]
    print(f"Run    : {journal.id}  ({journal.op}, {len(journal.ops):,} files)")
    print(f"Source : {journal.src_root}")
    print(f"Dest   : {journal.dest_root}")
    print(
        f"Action : {len(restorable):,} file(s) to reverse, {len(actions) - len(restorable):,} skipped"
    )
    for action in actions:
        if action.op == "skip":
            print(f"  skip    {action.dst}  ({action.note})")
        elif action.op == "restore" and action.dst:
            print(f"  restore {action.dst} -> {action.src}")
        elif action.dst:
            print(f"  delete  {action.dst}")
    if not restorable:
        print("\nNothing to reverse.")
        return 0
    if not args.apply:
        print("\nDry run - nothing reversed. Re-run with --apply to execute.")
        return 0
    with run_lock(journal_dir):
        count = apply_undo(journal, actions, journal_dir)
    print(f"\nReversed {count:,} file(s). Journal updated: {journal.path}")
    return 0


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Move drone capture folders into YYYY-MM-DD-Project-Name layout, with undo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "adapt is a dry run unless --apply is given; undo previews too.\n"
            "Install as a command with: uvs install tools/dji_incoming_renamer.py"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    adapt = sub.add_parser(
        "adapt",
        help="plan (and with --apply, perform) the move",
        description="Re-home files into <dest>/<YYYY-MM-DD>-<Project-Name>/<relative path>. "
        "Dry run unless --apply.",
    )
    adapt.add_argument(
        "src", help="source folder, e.g. W:\\Incoming\\Drones\\ELC\\2026-Aug"
    )
    adapt.add_argument(
        "-d",
        "--dest",
        help=f"destination root (default: ${DEST_ENV} or {DEFAULT_DEST})",
    )
    adapt.add_argument(
        "-p",
        "--project",
        help="project label for every file (overrides the pilot's flight name)",
    )
    adapt.add_argument(
        "--restyle",
        action="store_true",
        help="ignore how existing TIM folders spell a label, so --style can "
        "rename a project a second time",
    )
    adapt.add_argument(
        "--style",
        choices=["split", "camel", "verbatim"],
        default="split",
        help="label style: split=un-squish words (default), camel=camelCase only, "
        "verbatim=pilot's text exactly",
    )
    adapt.add_argument(
        "--date", type=parse_iso_date, help="force YYYY-MM-DD for every file"
    )
    adapt.add_argument(
        "--only-date",
        type=parse_iso_date,
        action="append",
        metavar="YYYY-MM-DD",
        help="only move files for this date (repeatable)",
    )
    adapt.add_argument(
        "--include-misc",
        action="store_true",
        help="also move MISC/ (thumbnails, DJI db)",
    )
    adapt.add_argument(
        "--exclude",
        action="append",
        metavar="GLOB",
        help="skip matching files (repeatable)",
    )
    adapt.add_argument(
        "--on-conflict",
        choices=["skip", "rename", "overwrite"],
        default="skip",
        help="what to do when the destination file exists (default: skip)",
    )
    adapt.add_argument(
        "--copy",
        action="store_true",
        help="copy instead of move (undo deletes the copies)",
    )
    adapt.add_argument("--apply", action="store_true", help="actually perform the plan")
    adapt.add_argument(
        "--keep-empty",
        action="store_true",
        help="do not prune source folders the move empties",
    )
    adapt.add_argument(
        "--prune-root",
        action="store_true",
        help="also remove the source folder itself when the move empties it",
    )
    adapt.add_argument(
        "--dry-run",
        action="store_true",
        help="explicitly do not perform the plan (default)",
    )
    adapt.add_argument("--journal-dir", help="where run journals live")
    adapt.set_defaults(func=cmd_adapt)

    undo = sub.add_parser(
        "undo",
        help="reverse a previous run",
        description="Reverse a journaled run. Dry run unless --apply.",
    )
    undo.add_argument(
        "--run", help="run id (or unique prefix); default is the latest applied run"
    )
    undo.add_argument(
        "--last", action="store_true", help="reverse the latest applied run (default)"
    )
    undo.add_argument("--list", action="store_true", help="list runs instead")
    undo.add_argument(
        "--force", action="store_true", help="reverse a run already marked undone"
    )
    undo.add_argument("--apply", action="store_true", help="actually reverse")
    undo.add_argument("--journal-dir", help="where run journals live")
    undo.set_defaults(func=cmd_undo)

    runs = sub.add_parser("runs", help="list journaled runs")
    runs.add_argument("--limit", type=int, default=20)
    runs.add_argument("--json", action="store_true")
    runs.add_argument("--journal-dir", help="where run journals live")
    runs.set_defaults(func=cmd_runs)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    try:
        return int(args.func(args) or 0)
    except LockError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
