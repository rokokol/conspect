# Digitization toolkit

Tools for the digitization of a course whose lectures are on video: download, transcription, a second listen to a disputed window, board frames. The process, the agent briefs and the acceptance rules are in the vault skill [`digitize`](../../../.agents/skills/digitize/SKILL.md)

## Work folder

All tools read a work folder from `DIGI_WORK`. Keep it outside the vault, for example `~/.cache/<course>-digitization/`. It holds `audio/LNN.mp3`, `video/LNN.mp4`, `transcripts/`, `logs/` and, optionally, `subs/`. The work folder is scaffolding: delete it when the course is done

## Tools

| File | What it does |
| --- | --- |
| `run-whisper.sh <first> <last>` | transcribes each lecture as its audio finishes, then repairs hallucinated windows (`../transcribe.py`, `../repair.py`); needs `DIGI_VENV` |
| `listen.sh NN MM:SS MM:SS` | prints six readings of a disputed window (`../listen.py`); confirms a lecturer's slip, because Whisper drops words |
| `frame.sh NN MM:SS` | extracts one board frame from the video |
| `vtt2txt.py subs/LNN.ru-orig.vtt` | turns YouTube auto-subs into `[HH:MM:SS]` lines; times are right, words are poor |

`DIGI_VENV` is a venv with `faster-whisper` and the `nvidia-cudnn-cu12` and `nvidia-cublas-cu12` wheels. Make it with `uv venv --python 3.12 <venv>`, then `UV_HTTP_TIMEOUT=120 uv pip install faster-whisper nvidia-cudnn-cu12 nvidia-cublas-cu12`; PyPI is slow, so repeat the install when it times out. `DIGI_HOTWORDS` lists the terms of the course for Whisper, English terms in Latin script

On NixOS the GPU is visible only with the driver `libcuda.so` from `/run/opengl-driver/lib`; `run-whisper.sh` sets the path. When the transcription is slow, check the device count: `python -c "import ctranslate2; print(ctranslate2.get_cuda_device_count())"` with the same `LD_LIBRARY_PATH` must print `1`

Download: `yt-dlp -f bestaudio -x --audio-format mp3` for audio, `-f "bv*[height<=480]"` for video, `--write-auto-subs --sub-langs ru-orig --skip-download` for subs. A download that fails with HTTP 403 works on a repeat
