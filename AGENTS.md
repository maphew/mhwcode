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

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.
<!-- END BEADS CODEX SETUP -->
