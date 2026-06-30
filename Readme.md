# Matt's code thicket

A sometimes-tended garden of things a _hewer of maps_ has made and copied that
can occasionally be turned to useful work.

## Quick start

Most Python scripts run with [uv](https://docs.astral.sh/uv/) and need no
prior setup:

```
uv run tools/gitignore_to_fossil.py .gitignore
uv run gis/get-fgdb-stats.py path/to/data.gdb
uv run video/extract_poster_frames.py holiday.mp4 --contact-sheet
```

Scripts that require ArcGIS Pro, Windows registry access, or other managed
environments note their prerequisites in their own headers.

## Folder map

| Folder | Contents |
|---|---|
| `gis/` | GIS, ArcGIS, GDAL, QGIS, DEM and geospatial conversion tools |
| `arcplus/` | ArcGIS Desktop helper modules and toolbox scripts (Python 2 / arcpy) |
| `tools/` | Ready-to-run general utilities; see `tools/Readme.md` |
| `video/` | Video-processing helpers (poster-frame extraction, etc.) |
| `metril/` | OneNote → Trilium migration helpers |
| `register-python/` | Windows Python registry inspection and registration helpers |
| `other/` | Assorted Windows, shell, PDF, media, and admin scripts |
| `Lib/` | Reusable Python helpers (e.g. `pyuac.py` for UAC elevation) |
| `scrapbook/` | Experiments and reference snippets |
| `llm/` | LLM / AI workflow helpers |

## Requirements

- **Python 3.10+** for modern scripts; older scripts in `arcplus/` and
  `register-python/` were written for Python 2 / ArcGIS Desktop 10.x
- **[uv](https://docs.astral.sh/uv/)** — handles per-script dependencies
  declared via PEP 723 inline metadata (`# /// script … ///` blocks)
- **ArcGIS Pro** (optional) — needed by `arcplus/report-versions.py` and
  other `arcplus/` scripts
- **fiona, typer, rich, openpyxl** — pulled automatically by `uv run` for
  `gis/get-fgdb-stats.py`

## Code quality

[ruff](https://docs.astral.sh/ruff/) is configured in `ruff.toml`. Run it on
any script before committing:

```
uv tool run ruff check path/to/script.py
uv tool run ruff format path/to/script.py
```
