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

### checkpoint-vpn-service-toggle.ps1

Manage the Check Point Endpoint VPN services (`TracSrvWrapper`, `EPWD`).
With no argument shows current status.

```powershell
powershell -File checkpoint-vpn-service-toggle.ps1 [stop|start|restart]
```

Requires: Check Point Endpoint Connect installed; run as Administrator.

