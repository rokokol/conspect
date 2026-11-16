#!/usr/bin/env bash
# Re-listen disputed windows of a lecture: listen.sh 08 41:00 41:20 [start end ...]
# Prints six readings of each window. $DIGI_WORK holds audio/LNN.mp3 and transcripts/,
# $DIGI_VENV is a Python venv with faster-whisper (see ../listen.py).
set -euo pipefail
work=${DIGI_WORK:?set DIGI_WORK to the digitization work folder}
venv=${DIGI_VENV:?set DIGI_VENV to a venv with faster-whisper}
here=$(cd "$(dirname "$0")" && pwd)
lec=L$(printf '%02d' "$((10#$1))"); shift
export LECTURE_AUDIO="$work/audio" LECTURE_TRANSCRIPTS="$work/transcripts"
cd "$here/.."
exec "$venv/bin/python" listen.py "$lec" "$@"
