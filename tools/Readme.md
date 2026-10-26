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

Sort a pilot's DJI drop-off into the `TIM` processing queue, with a journaled
undo. The folder is renamed to `YYYY-MM-DD-<flight name>`; the individual files
inside are untouched:

```
W:\Incoming\Drones\ELC\2026-Aug\DCIM\DJI_202608101454_011_2bdominionremap\...
  -> W:\Incoming\Drones\TIM\2026-08-10-2b-Dominion-Remap\DCIM\DJI_202608101454_011_2bdominionremap\...
```

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

The date comes from the flight folder name, the file name, the nearest dated
ancestor folder, or finally the file mtime (announced in the plan). `MISC/` is
left alone unless `--include-misc`, in which case it follows the earliest date
group. The source folder you point at survives an emptied run unless you pass
`--prune-root`; emptied folders below it are pruned (disable with
`--keep-empty`).

```
dji-incoming-renamer adapt "W:\Incoming\Drones\ELC\2026-Aug"          # preview
uv run tools/dji_incoming_renamer.py adapt "...\2026-Aug" --apply       # do it
dji-incoming-renamer adapt "...\2026-Aug" -p "Cowley Creek" --apply     # force label
dji-incoming-renamer runs                                                # list runs
dji-incoming-renamer undo --last                                         # preview undo
dji-incoming-renamer undo --last --apply                                 # restore
```

Preview is the default for both `adapt` and `undo`; nothing moves until
`--apply`, and passing `--dry-run` always wins. Every run writes a JSON journal
(default `%LOCALAPPDATA%\dji-incoming-renamer\journal`, override with
`--journal-dir` or `DJI_INCOMING_RENAMER_JOURNAL`) so any run can be reversed
later, even after a reboot. `--on-conflict overwrite` parks the replaced file
beside the new one as `*.replaced-<run>` so undo can put it back. A lock file in
the journal directory stops two runs from interleaving.

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

