"""The course root, defined once for every script in this folder.

Python scripts import COURSE; shell scripts run this file and read the printed path.
Importing this module also puts the vault's shared ddlc figure theme
(01. Data/04. Scripts/ddlc_figures) on sys.path, so a script can `import ddlc_theme`.
"""
import sys
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1]
VAULT = COURSE.parents[2]
sys.path.insert(0, str(VAULT / "01. Data" / "04. Scripts" / "ddlc_figures"))

if __name__ == "__main__":
    print(COURSE)
