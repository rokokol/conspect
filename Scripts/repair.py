"""Re-transcribe windows where Whisper hallucinated instead of speech.

Whisper large-v3 sometimes emits a stock phrase ("Субтитры делал DimaTorch",
"Продолжение следует...") for a whole 30 s window and loses the speech in it.
It also loops on one phrase, or leaves a long window with a few words. This
finds such lines, transcribes each again together with one neighbour line on
each side, with a soft VAD and the preceding text as prompt, and splices the
result in with absolute timestamps. A window whose redo is no better is kept
and reported, never silently dropped.

Usage: python repair.py L02 [L03@0:59:22-0:59:48 ...]
The @window form redoes the rows that start inside it even if they look fine.
Settings ($LECTURE_AUDIO and others) are those of transcribe.py.
"""
import re
import sys

from faster_whisper import WhisperModel

from transcribe import CACHE, HOTWORDS, OUT, hms, load_audio

# Whole-line stock phrases only: a word like "редактор" can be real speech.
STOCK = re.compile(r"^\s*(субтитры (делал|создавал|сделал)|продолжение следует|"
                   r"редактор субтитров|корректор |спасибо за просмотр|"
                   r"подписывайтесь на канал|подпишитесь на канал).*$|dimatorch", re.I)
# A phrase of 1-4 words repeated five times or more in a row, 40+ characters
# in all, is a decoder loop. The lecturer's own "тан-тан-тан" stays shorter.
# Letters outside Cyrillic and Latin (Hangul, CJK and so on) mark noise decoded as speech.
FOREIGN = re.compile(r"[^\W\d_a-zA-Zа-яА-ЯёЁ]")
LOOP = re.compile(r"(\b\w+(?:\W+\w+){0,3}\W+)\1{4,}", re.I)


def looped(text):
    m = LOOP.search(text + " ")
    return bool(m) and len(m.group(0)) >= 40
LINE = re.compile(r"\[(\d+):(\d+):(\d+)\] (.*)")
SR = 16000


def parse(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = LINE.match(line)
        if m:
            h, mi, s, text = m.groups()
            rows.append((int(h) * 3600 + int(mi) * 60 + int(s), text))
    return rows


def sparse(rows, i, min_gap=20, min_rate=3.0):
    """A long window that holds too little text: speech was likely skipped.
    Normal speech here runs at 12-15 characters a second."""
    if i + 1 >= len(rows):
        return False
    gap = rows[i + 1][0] - rows[i][0]
    return gap >= min_gap and len(rows[i][1]) / gap < min_rate


def secs(hms_text):
    h, m, s = map(int, hms_text.split(":"))
    return h * 3600 + m * 60 + s


def force(rows, a, b):
    """Merge rows starting in [a, b) into one row to be redone unconditionally."""
    inside = [i for i, (t, _) in enumerate(rows) if a <= t < b]
    if not inside:
        raise SystemExit(f"no rows start inside {hms(a)}-{hms(b)}")
    i, j = inside[0], inside[-1]
    merged = (rows[i][0], " ".join(t for _, t in rows[i:j + 1]))
    return rows[:i] + [merged] + rows[j + 1:], i


def main():
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    for arg in sys.argv[1:]:
        # "L03" repairs detected windows; "L03@0:59:22-0:59:48" also redoes that window.
        lec, _, window = arg.partition("@")
        path = OUT / f"{lec}.whisper.txt"
        rows = parse(path)
        forced = set()
        if window:
            a, b = (secs(x) for x in window.split("-"))
            rows, k = force(rows, a, b)
            forced.add(k)
        def junk(i):
            return i in forced or bool(STOCK.search(rows[i][1])) or looped(rows[i][1])

        bad = [i for i in range(len(rows)) if junk(i) or sparse(rows, i)]
        if not bad:
            print(f"{lec}: clean", flush=True)
            continue
        # Redo each bad row together with one neighbour on each side, so the
        # cut never falls inside a phrase; overlapping groups merge.
        groups = []
        for i in bad:
            a, b = max(0, i - 1), min(len(rows) - 1, i + 1)
            if groups and a <= groups[-1][1] + 1:
                groups[-1][1] = max(groups[-1][1], b)
            else:
                groups.append([a, b])
        audio = load_audio(CACHE / f"{lec}.mp3")
        replace, still = {}, []
        for a, b in groups:
            t0 = rows[a][0]
            t1 = rows[b + 1][0] if b + 1 < len(rows) else len(audio) // SR
            prompt = " ".join(t for k, (_, t) in enumerate(rows[max(0, a - 3):a], max(0, a - 3))
                              if not junk(k))
            # A soft VAD splits the window at pauses: without it one segment
            # may span a minute and the decoder truncates its text.
            segs, _ = model.transcribe(
                audio[t0 * SR:t1 * SR], language="ru", beam_size=5,
                vad_filter=True, vad_parameters={"threshold": 0.25, "min_silence_duration_ms": 300},
                condition_on_previous_text=False, hotwords=HOTWORDS,
                initial_prompt=prompt[-500:] or None,
            )
            new = [(t0 + int(s.start), s.text.strip()) for s in segs]
            new = [(x, y) for x, y in new
                   if y and not STOCK.search(y) and not looped(y) and not FOREIGN.search(y)]
            kept = sum(len(rows[k][1]) for k in range(a, b + 1) if not junk(k))
            # Accept unless the redo lost a fifth of the real speech it replaces.
            if new and sum(len(y) for _, y in new) >= 0.8 * kept:
                replace[a] = (b, new)
                print(f"{lec}: {hms(t0)}-{hms(t1)} repaired, {len(new)} segments", flush=True)
            else:
                still.append(hms(t0))
        out, i = [], 0
        while i < len(rows):
            if i in replace:
                b, new = replace[i]
                out.extend(new)
                i = b + 1
            else:
                out.append(rows[i])
                i += 1
        tmp = path.with_suffix(".tmp")
        tmp.write_text("\n".join(f"[{hms(a)}] {b}" for a, b in out) + "\n", encoding="utf-8")
        tmp.rename(path)
        print(f"{lec}: DONE repair, unresolved: {still or 'none'}", flush=True)


if __name__ == "__main__":
    main()
