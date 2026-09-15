#!/usr/bin/env bash
# Cross-platform speak launcher for macOS and Linux

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYER_SCRIPT="$SCRIPT_DIR/stream_tts.py"
LOCK_FILE="$SCRIPT_DIR/speak.lock"

TEXT="${1:-}"
VOICE="${2:-eponine}"
TTS_URL="${3:-http://localhost:8000/tts}"
MODE="${4:-safe}"
VOLUME="${5:-1.5}"
AGENT_NAME="${6:-}"
OUTFILE="${7:-}"
NOPLAY="${8:-0}"

if [ -z "$TEXT" ]; then
    echo "[speak] Error: text argument is required." >&2
    exit 0
fi

# Auto-start pocket-tts if server is offline
HEALTH_URL="${TTS_URL%/tts}/health"
if ! curl -s --max-time 1 "$HEALTH_URL" | grep -q "healthy"; then
    if command -v pocket-tts >/dev/null 2>&1; then
        pocket-tts serve >/dev/null 2>&1 &
        sleep 2
    elif command -v uvx >/dev/null 2>&1; then
        uvx pocket-tts serve >/dev/null 2>&1 &
        sleep 2
    fi
fi

export TTS_TEXT="$TEXT"
export TTS_VOICE="$VOICE"
export TTS_URL="$TTS_URL"
export TTS_MODE="$MODE"
export TTS_AGENT="$AGENT_NAME"
export TTS_LOCKFILE="$LOCK_FILE"
export TTS_VOLUME="$VOLUME"
export TTS_OUTFILE="$OUTFILE"
export TTS_NOPLAY="$NOPLAY"

# Prevent OpenBLAS/OpenMP parallel thread contention
export OPENBLAS_NUM_THREADS=1
export GOTO_NUM_THREADS=1
export OMP_NUM_THREADS=1

if command -v uv >/dev/null 2>&1; then
    uv run \
        --with sounddevice \
        --with requests \
        --with numpy \
        "$PLAYER_SCRIPT" >/dev/null 2>&1 &
else
    # Fallback to direct python3 if uv is not installed
    python3 "$PLAYER_SCRIPT" >/dev/null 2>&1 &
fi
