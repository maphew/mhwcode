# Repository Guidelines

## Project Structure & Module Organization

This repository is a utility-script collection, not a single packaged application. Top-level directories group scripts by domain:

- `gis/`: GIS, ArcGIS, GDAL, QGIS, DEM, and geospatial conversion tools.
- `arcplus/`: ArcGIS helper modules and toolbox scripts.
- `tools/`: ready-to-run general utilities; see `tools/Readme.md`.
- `register-python/`: Windows Python registry inspection and registration helpers.
- `other/`: assorted Windows, shell, PDF, media, and admin scripts.
- `video/`: video-processing helpers such as poster-frame extraction.
- `Lib/`: reusable Python helpers.

Keep new scripts near related tools. If a script needs sample data, fixtures, or screenshots, place them in a local `samples/`, `assets/`, or clearly named sibling directory.

## Build, Test, and Development Commands

There is no repository-wide build or test command. Run tools directly from their directory and document any new dependencies beside the script.

- `uv run tools/gitignore_to_fossil.py`: run a Python utility with `uv`.
- `python video/extract_poster_frames.py --help`: inspect script usage.
- `powershell -File win-remote-reboot.ps1`: run a PowerShell script.
- `cmd /c other\bats\search-path.bat`: run a Windows batch helper.
- `pip install -r other/pdf-extract/requirements.txt`: install dependencies for the PDF extraction tools.

Avoid adding root-level package tooling unless it applies to the whole repository.

## Coding Style & Naming Conventions

Match the style of the directory you edit. Python scripts generally use 4-space indentation, descriptive snake_case names, and standard-library-first imports. PowerShell scripts use verb-noun names where practical, such as `Install-*` or `Update-*`. Batch and shell scripts should keep command side effects explicit and include short usage comments when arguments are not obvious.

Prefer portable paths in documentation, but preserve Windows-specific behavior in scripts that target Windows administration or ArcGIS Desktop workflows.

## Testing Guidelines

No shared test framework is configured. For changes, perform the smallest safe verification: run `--help`, execute against sample input, or dry-run the external command where supported. For GIS and registry tools, document required software, privileges, and manual verification steps in the script header or local README.

## Commit & Pull Request Guidelines

Recent history uses short imperative or scoped messages, for example `script: Install GDAL...`, `refactor: replace VPN toggle...`, and `wip: extract stills from video`. Prefer concise commit subjects that name the affected tool or intent.

Pull requests should describe the changed script, expected environment, verification performed, and any required external tools such as ArcGIS, GDAL, QGIS, `uv`, or Windows PowerShell. Include screenshots only for visual GIS or UI-facing documentation changes.
