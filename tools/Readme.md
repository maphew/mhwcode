# Tools

Ready-to-run scripts. All use [uv](https://docs.astral.sh/uv/) with inline
PEP 723 metadata, so dependencies install automatically on first run.

## Scripts

### gitignore_to_fossil.py

Convert `.gitignore` patterns to Fossil's ignore-glob format with a
side-by-side comparison. Optionally shows the shell commands to apply them.

```
uv run gitignore_to_fossil.py [.gitignore_file]
uv run gitignore_to_fossil.py --help
```

Requires: `rich` (declared inline; installed by `uv run` automatically).

### dji_incoming_renamer.py

Give a pilot's DJI drop-off the `YYYY-MM-DD-<flight name>` folder name, in
place, with a journaled undo. It is one `rename()` per capture folder: nothing
moves, and the individual files inside are untouched.

```
W:\Incoming\Drones\ELC\2026-Aug\DCIM\DJI_202608051635_001_01ClearCreek1\...
  -> W:\Incoming\Drones\ELC\2026-Aug\DCIM\2026-08-05-01-Clear-Creek-1\...
```

Because only directory entries are read (no tree walk, no per-file `stat`), a
card of 9,000 files previews in well under a second over SMB. Point it at the
month folder or straight at its `DCIM`; it looks at the top-level capture
folders and nothing deeper.

The flight name is the pilot's own mission name with DJI's
`<brand>_<YYYYMMDDHHMM>_<flight index>_` prefix removed, then un-squished into
words:

| flight folder | label |
|---|---|
| `..._011_2bdominionremap` | `2b-Dominion-Remap` |
| `..._001_01ClearCreek1` | `01-Clear-Creek-1` |
| `..._003_Create-Area-Route2` | `Create-Area-Route-2` |
| `..._012_1-Dominion` | `1-Dominion` |

Splitting learns from the archive: existing `TIM/<date>-<label>` folders supply
the place names and mission words actually in use, so `Pondy-Pit` splits ("pondy"
is not English) while `Mendenhall` and `Nunatuk` are left whole. A label that is
already archived also keeps the archive's exact spelling, so re-importing a
mission cannot create a second, differently-hyphenated folder; `--restyle`
ignores that and renames anyway. `--style camel` splits only on camelCase,
`--style verbatim` keeps the pilot's text as typed (only path-illegal characters
changed), and `--project` overrides every label.

#### Repeated flights of one mission

DJI opens a new folder every time a flight is interrupted and resumed (battery
swap, land/reposition/take-off), keeping the mission's start time in the name.
One mission can arrive as several folders, with file numbering restarting at
`0001` in each:

```
DJI_202608091625_008_Create-Area-Route7    79 shots  16:32:48-16:33:43
DJI_202608091625_009_Create-Area-Route7    58 shots  16:37:15-16:37:55
DJI_202608091625_010_Create-Area-Route7   952 shots  16:41:16-16:52:27
```

That is one continuous mission, not duplicate data, and the folders cannot be
merged without colliding file names. Each is renamed separately, in DJI's flight
order, with a zero-padded suffix:

```
2026-08-09-Create-Area-Route-7
2026-08-09-Create-Area-Route-7-02
2026-08-09-Create-Area-Route-7-03
```

Two digits because a mission can split more than nine ways (one already has
six folders in the archive): unpadded, `-10` sorts before `-02` and the flights
come back out of order.

A taken name never costs you a folder: it grows a suffix rather than being
skipped, and no folder is ever overwritten (`--on-conflict overwrite` is refused
in place). If an earlier run already left `…-02` behind, the new flights keep
counting up from it (`…-03`, `…-04`) rather than becoming `…-02-2`.
`--on-conflict skip` leaves later flights under their DJI names instead of
suffixing them.

The date comes from the flight folder name, a dated ancestor folder, or finally
the folder's own mtime (announced in the plan). `MISC/` and other container
folders are left alone in place; they only travel with `--dest --include-misc`.

#### Relocating into TIM instead

`--dest W:\Incoming\Drones\TIM` still moves files into
`<dest>/<date>-<label>/<relative path>` rather than renaming folders. That needs
the file tree, so it is slower, and it prunes the folders it empties (disable
with `--keep-empty`; `--prune-root` also removes the folder you pointed at).

```
dji-incoming-renamer adapt "W:\Incoming\Drones\ELC\2026-Aug"          # preview
uv run tools/dji_incoming_renamer.py adapt "...\2026-Aug" --apply       # do it
uv run tools/dji_incoming_renamer.py adapt "...\2026-Aug\DCIM" --apply  # same, pointed at DCIM
dji-incoming-renamer adapt "...\2026-Aug" -p "Cowley Creek" --apply     # force label
dji-incoming-renamer adapt "...\2026-Aug" -d "W:\Incoming\Drones\TIM"  # relocate instead
dji-incoming-renamer runs                                                # list runs
dji-incoming-renamer undo --last                                         # preview undo
dji-incoming-renamer undo --last --apply                                 # restore
```

Preview is the default for both `adapt` and `undo`; nothing changes until
`--apply`, and passing `--dry-run` always wins. Every run writes a JSON journal
(default `%LOCALAPPDATA%\dji-incoming-renamer\journal`, override with
`--journal-dir` or `DJI_INCOMING_RENAMER_JOURNAL`) so any run can be reversed
later, even after a reboot, and a lock file in the journal directory stops two
runs from interleaving. In relocation mode `--on-conflict overwrite` parks the
replaced file beside the new one as `*.replaced-<run>` so undo can put it back.

Undo never guesses in a direction that can lose data. It is recorded per folder,
so a crash or a half-finished `undo` is resumable, and anything it cannot do
safely is reported as **blocked** (the run stays `partial`, and a later
`undo --last` retries it) rather than silently counted as reversed:

- a name taken by someone else, a folder this run never renamed, a different
  folder now wearing the renamed name, a location that is not mounted;
- restoring a `*.replaced-<run>` backup whose name is occupied leaves the backup
  beside it for you to look at;
- nothing is ever moved across volumes by undo, and nothing is ever nested
  inside an existing folder.

`--force` reverses a run already marked undone and moves a folder back even when
file identity says it is no longer the folder that run renamed.

Requires: Python 3.10+ and `wordninja` (declared inline; installed by `uv run`
automatically). Installed as a command with
`uvs install tools/dji_incoming_renamer.py` (tool name `dji-incoming-renamer`);
run `uvs update tools/dji_incoming_renamer.py` after editing the script.

### checkpoint-vpn-service-toggle.ps1

Manage the Check Point Endpoint VPN services (`TracSrvWrapper`, `EPWD`).
With no argument shows current status.

```powershell
powershell -File checkpoint-vpn-service-toggle.ps1 [stop|start|restart]
```

Requires: Check Point Endpoint Connect installed; run as Administrator.

