"""Transcribe lecture audio with faster-whisper large-v3 on GPU.

Usage: python transcribe.py L01 [L02 ...]
Audio: $LECTURE_AUDIO/<L>.mp3
Output: $LECTURE_TRANSCRIPTS/<L>.whisper.txt, lines "[HH:MM:SS] text".
$LECTURE_HOTWORDS (optional): comma-separated terms the lecturer says in English,
so Whisper writes "ROC-AUC" rather than a Cyrillic guess.
Audio is decoded by ffmpeg, because faster-whisper 1.2.1 fails with PyAV 19.
repair.py and listen.py take the same settings from here.
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def _dir(var):
    if not os.environ.get(var):
        raise SystemExit(f"set {var} to a folder (see the docstring of transcribe.py)")
    return Path(os.environ[var]).expanduser()


CACHE = _dir("LECTURE_AUDIO")
OUT = _dir("LECTURE_TRANSCRIPTS")
HOTWORDS = os.environ.get("LECTURE_HOTWORDS") or None


def load_audio(path: Path) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-f", "f32le", "-ac", "1",
         "-ar", "16000", "-loglevel", "error", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, np.float32)


def hms(t: float) -> str:
    t = int(t)
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def main() -> None:
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    OUT.mkdir(parents=True, exist_ok=True)
    for lec in sys.argv[1:]:
        dst = OUT / f"{lec}.whisper.txt"
        if dst.exists():
            print(f"{lec}: exists, skip", flush=True)
            continue
        segments, _ = model.transcribe(
            load_audio(CACHE / f"{lec}.mp3"), language="ru", vad_filter=True,
            beam_size=5, condition_on_previous_text=False, hotwords=HOTWORDS,
        )
        lines = []
        for s in segments:
            lines.append(f"[{hms(s.start)}] {s.text.strip()}")
            if len(lines) % 200 == 0:
                print(f"{lec}: {hms(s.start)}", flush=True)
        tmp = dst.with_suffix(".tmp")
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        tmp.rename(dst)
        print(f"{lec}: DONE {len(lines)} segments", flush=True)


if __name__ == "__main__":
    main()
