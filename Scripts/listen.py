"""Re-listen a disputed window of a lecture several ways and print every reading.

ASR on a single pass can drop a "не" or swap a word; agreement across
readings with different context, beam and temperature decides it. Nothing is
written: the readings go to stdout for a person or a verifier to judge.

Usage: python listen.py L02 1:26:10 1:26:25 [more windows as start end pairs]
Settings ($LECTURE_AUDIO and others) are those of transcribe.py.
"""
import os
import sys
from pathlib import Path


def _cuda_env():
    """Re-run this script once with the CUDA libraries on LD_LIBRARY_PATH.

    ctranslate2 loads cuBLAS and cuDNN at start-up, so the path has to be set
    before the process begins; the NixOS driver lives in /run/opengl-driver.
    """
    if os.environ.get("LECTURE_CUDA_SET") == "1":
        return
    site = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    libs = ["/run/opengl-driver/lib", str(site / "nvidia/cudnn/lib"), str(site / "nvidia/cublas/lib")]
    env = dict(os.environ, LECTURE_CUDA_SET="1",
               LD_LIBRARY_PATH=":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")]).rstrip(":"))
    os.execve(sys.executable, [sys.executable, *sys.argv], env)


_cuda_env()

from faster_whisper import WhisperModel  # noqa: E402

from transcribe import CACHE, load_audio  # noqa: E402

SR = 16000
CONFIGS = [(5, 0.0), (10, 0.0), (5, 0.4)]
PADS = [(0, 0), (8, 4), (20, 8)]  # extra seconds of context before and after


def secs(t):
    parts = [int(p) for p in t.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def main():
    lec, *bounds = sys.argv[1:]
    if not bounds or len(bounds) % 2:
        raise SystemExit(__doc__)
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    audio = load_audio(CACHE / f"{lec}.mp3")
    for a, b in zip(bounds[::2], bounds[1::2]):
        t0, t1 = secs(a), secs(b)
        print(f"=== {lec} {a}-{b}")
        for before, after in PADS:
            s0, s1 = max(0, t0 - before), t1 + after
            for beam, temp in CONFIGS:
                segs, _ = model.transcribe(audio[s0 * SR:s1 * SR], language="ru", vad_filter=False,
                                           beam_size=beam, temperature=temp,
                                           condition_on_previous_text=False)
                text = " ".join(s.text.strip() for s in segs)
                print(f"[-{before}s +{after}s beam {beam} T {temp}] {text}", flush=True)


if __name__ == "__main__":
    main()
