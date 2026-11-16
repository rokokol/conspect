#!/usr/bin/env bash
# Extract one board frame from a lecture video: frame.sh 09 12:34
# Writes $DIGI_WORK/frames/L09-12m34s.png and prints its path.
# $DIGI_WORK holds video/LNN.mp4, one file per lecture.
set -euo pipefail
work=${DIGI_WORK:?set DIGI_WORK to the digitization work folder}
lec=$(printf '%02d' "$((10#$1))")
t=$2
mkdir -p "$work/frames"
out="$work/frames/L$lec-${t//:/m}s.png"
ffmpeg -nostdin -loglevel error -y -ss "$t" -i "$work/video/L$lec.mp4" -frames:v 1 "$out"
echo "$out"
