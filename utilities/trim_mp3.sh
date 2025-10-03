#!/usr/bin/env bash
# -------------------------------------------------------------
# trim_mp3.sh — Quick MP3 trimmer with ffmpeg (WSL-friendly)
# -------------------------------------------------------------
# Windows NOTES:
# - Run this inside your WSL shell (Ubuntu/Debian).
# - ffmpeg must be installed in WSL (not Windows): 
#     sudo apt update && sudo apt install -y ffmpeg
# - If you edited this file in Windows and see weird behavior,
#   convert line endings:   sudo apt install -y dos2unix && dos2unix trim_mp3.sh
# - Paths with spaces work if quoted. Prefer placing files under
#   your Linux home (e.g., /home/you) to avoid permission/path issues.
#
# USAGE:
#   ./trim_mp3.sh -i input.mp3 -o output.mp3 -s 0.25            # trim from 0.25s to end (fast, no re-encode)
#   ./trim_mp3.sh -i input.mp3 -o output.mp3 -s 00:00:00.250    # same start, timestamp format
#   ./trim_mp3.sh -i input.mp3 -o output.mp3 -s 0.25 -d 1.8     # keep 1.8s from 0.25s
#   ./trim_mp3.sh -i input.mp3 -o output.mp3 -s 0.25 -d 1.8 -e  # force re-encode (frame-accurate)
#   ./trim_mp3.sh -i input.mp3 -o output.mp3 -s 0.25 -d 1.8 -f 20  # add 20ms fades (re-encodes)
#
# OPTIONS:
#   -i  Input audio file (MP3/WAV/etc.)
#   -o  Output audio file (usually .mp3)
#   -s  Start offset (seconds or HH:MM:SS.mmm)
#   -d  Duration to KEEP from start (optional)
#   -e  Force re-encode (accurate cuts; needed for filters/fades)
#   -f  Fade length in milliseconds (applies fade-in; if -d set, adds fade-out)
#
# HOW IT WORKS:
# - By default we try a stream copy (-c copy) for MP3: very fast & lossless,
#   but cuts only on frame boundaries (~26ms), i.e. not sample-accurate but 
#   good enough for most trims.
# - If sample-accurate cuts are needed, fades, filters, or you pass -e / -f,
#   we re-encode (slower, but precise).
#
# HANDY FFMPEG SNIPPETS (copy/modify as needed):
# ------------------------------------------------
# • Fade in/out:
#   ffmpeg -i in.mp3 -af "afade=t=in:st=0:d=0.05,afade=t=out:st=END-0.05:d=0.05" out.mp3
# • Volume +3 dB:
#     ffmpeg -i in.mp3 -filter:a "volume=3dB" out.mp3
# • Loudness normalize (EBU R128):
#     ffmpeg -i in.mp3 -filter:a "loudnorm" out.mp3
# • Speed up 15% (keeps pitch):
#     ffmpeg -i in.mp3 -filter:a "atempo=1.15" out.mp3
# • Quick pitch up ~1 semitone (re-encodes):
#     ffmpeg -i in.mp3 -filter:a "asetrate=48000*1.05946,aresample=48000" out.mp3
# • Concatenate MP3s (no re-encode):
#     printf "file 'a.mp3'\nfile 'b.mp3'\n" > list.txt
# • Convert MP3->WAV:
#   ffmpeg -i in.mp3 out.wav
#     ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp3
# • Remove leading silence (gate):
#     ffmpeg -i in.mp3 -af "silenceremove=start_periods=1:start_silence=0.2:start_threshold=-40dB" out.mp3
# ------------------------------------------------

set -euo pipefail

INPUT=""
OUTPUT=""
START=""
DURATION=""
FORCE_REENCODE=0
FADE_MS=0

usage() { grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 1; }

# --- Parse flags ---
while getopts ":i:o:s:d:ef:h" opt; do
  case ${opt} in
    i) INPUT="$OPTARG" ;;
    o) OUTPUT="$OPTARG" ;;
    s) START="$OPTARG" ;;
    d) DURATION="$OPTARG" ;;
    e) FORCE_REENCODE=1 ;;
    f) FADE_MS="$OPTARG" ;;
    h|*) usage ;;
  esac
done

# --- Validate args ---
[[ -z "${INPUT}" || -z "${OUTPUT}" || -z "${START}" ]] && usage

# --- Check ffmpeg availability (WSL) ---
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "❌ ffmpeg not found in WSL. Install with: sudo apt update && sudo apt install -y ffmpeg" >&2
  exit 1
fi

# --- Decide whether we must re-encode ---
# We must re-encode if user requested it (-e) or wants fades (-f > 0).
NEED_REENCODE=$FORCE_REENCODE
if [[ "${FADE_MS}" -gt 0 ]]; then
  NEED_REENCODE=1
fi

# --- Build filter chain if fading ---
AFILTER=""
if [[ "${FADE_MS}" -gt 0 ]]; then
  # Always fade in at start for FADE_MS ms.
  AFILTER="afade=t=in:st=0:d=$(awk "BEGIN{print ${FADE_MS}/1000}")"
  # If we know duration (-d), add a matching fade out at the end.
  if [[ -n "${DURATION}" ]]; then
    # fade-out start time = duration - fade_ms
    FO_ST=$(awk "BEGIN{print ${DURATION}-${FADE_MS}/1000}")
    AFILTER="${AFILTER},afade=t=out:st=${FO_ST}:d=$(awk "BEGIN{print ${FADE_MS}/1000}")"
  fi
fi

# --- Run ffmpeg ---
if [[ "${NEED_REENCODE}" -eq 1 ]]; then
  # Re-encode path: accurate trims; applies filters (fades) if any.
  if [[ -n "${DURATION}" ]]; then
    if [[ -n "${AFILTER}" ]]; then
      ffmpeg -hide_banner -loglevel error -ss "${START}" -t "${DURATION}" -i "${INPUT}" \
             -af "${AFILTER}" -y "${OUTPUT}"
    else
      ffmpeg -hide_banner -loglevel error -ss "${START}" -t "${DURATION}" -i "${INPUT}" \
             -y "${OUTPUT}"
    fi
  else
    # No duration → from START to end
    if [[ -n "${AFILTER}" ]]; then
      ffmpeg -hide_banner -loglevel error -ss "${START}" -i "${INPUT}" \
             -af "${AFILTER}" -y "${OUTPUT}"
    else
      ffmpeg -hide_banner -loglevel error -ss "${START}" -i "${INPUT}" -y "${OUTPUT}"
    fi
  fi
else
  # Stream-copy path: very fast, no quality loss; not sample-accurate.
  if [[ -n "${DURATION}" ]]; then
    ffmpeg -hide_banner -loglevel error -ss "${START}" -t "${DURATION}" -i "${INPUT}" \
           -c copy -y "${OUTPUT}" || {
      echo "⚠️  Stream copy failed; retrying with re-encode for precision..."
      ffmpeg -hide_banner -loglevel error -ss "${START}" -t "${DURATION}" -i "${INPUT}" -y "${OUTPUT}"
    }
  else
    ffmpeg -hide_banner -loglevel error -ss "${START}" -i "${INPUT}" -c copy -y "${OUTPUT}" || {
      echo "⚠️  Stream copy failed; retrying with re-encode for precision..."
      ffmpeg -hide_banner -loglevel error -ss "${START}" -i "${INPUT}" -y "${OUTPUT}"
    }
  fi
fi

echo "✅ Wrote ${OUTPUT}"
