"""Turn YouTube auto-sub VTT files into compact "[HH:MM:SS] text" lines, one per ~20 s.

Usage: python vtt2txt.py subs/L01.ru-orig.vtt ...  ->  subs/L01.txt
"""
import re
import sys
from pathlib import Path

CUE = re.compile(r"^(\d\d):(\d\d):(\d\d)\.\d+ --> ")
TAG = re.compile(r"<[^>]+>")

for src in map(Path, sys.argv[1:]):
    rows, seen, start, words = [], set(), None, []
    t = 0
    for line in src.read_text(encoding="utf-8").splitlines():
        m = CUE.match(line)
        if m:
            h, mi, s = map(int, m.groups())
            t = h * 3600 + mi * 60 + s
            continue
        text = TAG.sub("", line).strip()
        if not text or text in seen or "-->" in text or text.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        seen.add(text)
        if start is None:
            start = t
        words.append(text)
        if t - start >= 20:
            rows.append(f"[{start // 3600:02d}:{start % 3600 // 60:02d}:{start % 60:02d}] {' '.join(words)}")
            start, words = None, []
    if words:
        rows.append(f"[{start // 3600:02d}:{start % 3600 // 60:02d}:{start % 60:02d}] {' '.join(words)}")
    dst = src.with_name(src.name.split(".")[0] + ".txt")
    dst.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(dst, len(rows))
