"""The course root, defined once for every figure script in this folder.

Scripts build their output paths from it: COURSE / "content" / "<topic>" / "00. Вложения".
Importing this module also puts the vault's shared ddlc figure modules
(Scripts/ddlc_figures) on sys.path, so theme.py can `import ddlc_fonts`.
"""
import sys
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1]
VAULT = COURSE.parents[0]
sys.path.insert(0, str(VAULT / "01. Data" / "04. Scripts" / "ddlc_figures"))
