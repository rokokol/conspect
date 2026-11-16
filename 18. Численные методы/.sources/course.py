"""The course root, defined once for every script in this folder.

Importing this module also puts the vault's shared ddlc figure theme
(Scripts/ddlc_figures) and the sandbox kit's parent on sys.path, so a script
can `import ddlc_theme` and `from sandbox_kit import page`.
Python scripts import COURSE; shell scripts run this file and read the printed path.
"""
import sys
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1]
VAULT = COURSE.parents[0]
SCRIPTS = VAULT / "Scripts"
sys.path.insert(0, str(SCRIPTS / "ddlc_figures"))
sys.path.insert(0, str(SCRIPTS))

if __name__ == "__main__":
    print(COURSE)
