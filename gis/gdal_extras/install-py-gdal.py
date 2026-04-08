# /// script
# requires-python = ">=3.12"
# ///
"""Install GDAL into the active uv environment from the mentaljam GDAL wheel index.

Fixes `uv add GDAL` broken on Windows or other systems that don't have a compiler (https://github.com/astral-sh/uv/issues/11466).

Script is self-contained and can used instead of `uv add GDAL` in any uv project.

  uv run install-py-gdal.py

        Installing GDAL from https://gitlab.com/api/v4/projects/61637378/packages/pypi/simple
        Resolved 1 package in 3.10s
        Prepared 1 package in 1.63s
        Installed 1 package in 1.23s
        + gdal==3.12.1
        Successfully imported gdal module version: 3.12.1

Specify python version and don't embed in current project:

    uv run --python 3.13 --no-project install-py-gdal.py
"""

from __future__ import annotations

import subprocess
import sys
import types

# Courtesy of https://gitlab.com/mentaljam/gdal-wheels
GDAL_SIMPLE_INDEX = "https://gitlab.com/api/v4/projects/61637378/packages/pypi/simple"


def install_gdal() -> None:
    if sys.platform not in {"win32", "linux"}:
        raise SystemExit(f"Unsupported platform: {sys.platform}")

    print(f"Installing GDAL from {GDAL_SIMPLE_INDEX}", flush=True)
    subprocess.check_call(
        [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
            "--default-index",
            GDAL_SIMPLE_INDEX,
            "--only-binary",
            "gdal",
            "gdal",
        ]
    )


def ensure_gdal() -> "types.ModuleType":
    try:
        from osgeo import gdal

        return gdal
    except ImportError:
        install_gdal()
        from osgeo import gdal

        return gdal


def main() -> None:
    gdal = ensure_gdal()
    version = gdal.VersionInfo("RELEASE_NAME")
    print(f"Successfully imported gdal module version: {version}")


if __name__ == "__main__":
    main()
