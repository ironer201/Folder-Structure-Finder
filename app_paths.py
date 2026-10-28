"""
app_paths.py

Filesystem helpers for exported output files.

Exports must land next to the program the user actually launched. In a
PyInstaller --onefile build that is the folder containing the executable, not
the current working directory (which depends on where/how it was started).
"""

import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """Return the directory of the running program.

    Frozen build -> the folder containing the executable (sys.executable).
    Source run   -> the current working directory.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()
