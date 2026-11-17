"""Cross-platform project tasks, using only the standard library.

Usage:
    python tasks.py setup    # create .venv and install requirements
    python tasks.py test     # run all tests and doctests
"""

import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"
IS_WINDOWS = os.name == "nt"
PYTHON = VENV / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python")


def run(*args: object) -> None:
    """Run a command from the project root, exiting cleanly if it fails."""
    result = subprocess.run([str(arg) for arg in args], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)


def setup() -> None:
    if not VENV.exists():
        venv.create(VENV, with_pip=True)
    run(PYTHON, "-m", "pip", "install", "-r", "requirements.txt")


def test() -> None:
    if not PYTHON.exists():
        sys.exit("No .venv found. Run: python tasks.py setup")
    run(PYTHON, "-m", "pytest")


TASKS = {"setup": setup, "test": test}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        sys.exit(__doc__)
    TASKS[sys.argv[1]]()
