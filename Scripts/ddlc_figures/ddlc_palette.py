"""The ddlc palette by name, read from the vendored palette.css: "--ddlc-monika-eye" -> P["monika-eye"].

Importing it changes no matplotlib setting, so a course that keeps its own look (Physics) takes
its colours from here without the rest of ddlc_theme.
"""
import re
from pathlib import Path

P = dict(re.findall(r"--ddlc-([a-z-]+):\s*(#[0-9A-Fa-f]{6})",
                    (Path(__file__).resolve().parent / "palette.css").read_text(encoding="utf-8")))
