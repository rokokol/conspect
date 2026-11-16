#!/usr/bin/env bash
# Transcribe every lecture as soon as its audio download finishes, then repair the transcript.
# Usage: run-whisper.sh <first> <last>      for example: run-whisper.sh 1 21
# Needs: DIGI_WORK (audio/LNN.mp3 and logs/download-audio.log with a line "LNN audio done"
#        per finished download), DIGI_VENV (venv with faster-whisper, cudnn and cublas wheels),
#        DIGI_HOTWORDS (comma-separated terms the lecturer says, optional).
set -euo pipefail
work=${DIGI_WORK:?set DIGI_WORK to the digitization work folder}
venv=${DIGI_VENV:?set DIGI_VENV to a venv with faster-whisper}
here=$(cd "$(dirname "$0")" && pwd)
site=$(echo "$venv"/lib/python3.*/site-packages)
export LD_LIBRARY_PATH="/run/opengl-driver/lib:$site/nvidia/cudnn/lib:$site/nvidia/cublas/lib"
export LECTURE_AUDIO="$work/audio" LECTURE_TRANSCRIPTS="$work/transcripts"
[ -n "${DIGI_HOTWORDS:-}" ] && export LECTURE_HOTWORDS="$DIGI_HOTWORDS"
cd "$here/.."
for n in $(seq -w "$1" "$2"); do
  until grep -q "^L$n audio done" "$work/logs/download-audio.log" 2>/dev/null; do sleep 20; done
  "$venv/bin/python" transcribe.py "L$n"
  "$venv/bin/python" repair.py "L$n" || echo "L$n: repair failed"
done
