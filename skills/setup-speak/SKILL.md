---
name: setup-speak
description: Interactive wizard to install a local TTS engine, audition voices, and configure agent speech preferences.
disable-model-invocation: true
---

Guide the user through setting up local text-to-speech for AI agents. Run this once per workstation or repository.

## Phase 1: Detect Operating System and Environment

Detect the host operating system before asking any questions:

- **Windows**: Use `uvx` for Pocket-TTS, Docker for Kokoro, or ONNX Runtime for Kitten TTS.
- **macOS (Apple Silicon)**: Use `uvx` for Pocket-TTS, `mlx-audio` for accelerated Kokoro, or ONNX Runtime for Kitten TTS.
- **macOS (Intel)**: Use `uvx` for Pocket-TTS, Docker for Kokoro, or pip for Kitten TTS.
- **Linux**: Use `uvx` for Pocket-TTS, Docker for Kokoro, or pip for Kitten TTS.

Confirm the detected platform to the user in one sentence and proceed to engine selection.

## Phase 2: Engine Selection

Present the three local neural engines clearly. Highlight their core trade-offs:

| Engine | Size | RAM Footprint | Key Strength |
|---|---|---|---|
| **Pocket-TTS** (Kyutai Labs) | ~100M params (150 MB) | ~300 MiB | Zero-shot voice cloning from a 5-second audio clip. Conversational cadence. MIT license. |
| **Kokoro-82M** (hexgrad) | 82M params (82 MB) | ~150 MiB | 54+ studio voices across 8 languages. High prosodic fidelity. Apache 2.0 license. |
| **Kitten TTS** (KittenML) | 15M to 80M (<25 MB) | ~30 MiB | Ultra-lightweight ONNX runtime. Minimal memory footprint. Apache 2.0 license. Note: Set speed to 1.25 for natural cadence. |

Ask the user which engine they want to configure.

## Phase 3: Engine Installation and Verification

Provide exact, copy-pasteable commands based on the selected engine and detected operating system:

### Option A: Pocket-TTS (Recommended for Conversational Identity)

```bash
# Permanent local installation with PATH executable (avoids ephemeral redownloads)
uv tool install pocket-tts

# Launch server (or let the speak driver auto-start it in the background)
pocket-tts serve
```

Verify the server is healthy by querying `http://localhost:8000/health`.

### Option B: Kokoro-82M (hexgrad)

**If using Docker (Containerized Server):**
```bash
# CPU container with persistent model and voice caching volumes
docker run -d --name kokoro-tts -p 8880:8880 \
  -v kokoro-models:/app/api/src/models \
  -v kokoro-voices:/app/api/src/voices \
  --restart unless-stopped \
  ghcr.io/remsky/kokoro-fastapi-cpu:latest
```
Verify by querying `http://localhost:8880/health`.

**If not using Docker (Pure ONNX Runtime):**
```bash
# Zero-Docker, Zero-PyTorch ONNX installation
pip install kokoro-onnx soundfile
```
*(Requires `espeak-ng`: `brew install espeak-ng` on macOS, `sudo apt install espeak-ng` on Linux, `winget install eSpeak-NG.eSpeak-NG` on Windows).*

### Option C: Kitten TTS (Pure ONNX)

```bash
# Zero-Docker, Zero-PyTorch ultra-lightweight installation (<25 MB)
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl soundfile onnxruntime
```

## Phase 4: Voice Audition (Demos)

Do not make the user guess what a voice sounds like from a list of names.

Generate a standardized greeting using the selected engine across 3 to 4 prominent candidate voices:

- **Standard test sentence**: `"Hello, I am your agent. I will keep you updated while you focus on deep work."`
- **Pocket-TTS candidates**: `eponine` (expressive female), `michael` (calm focus male), `caro_davy` (natural narrator), `javert` (authoritative male).
- **Kokoro candidates**: `af_heart` (clear American female), `am_fenrir` (deep American male), `bf_emma` (British female), `bm_george` (British male).
- **Kitten TTS candidates**: `Jasper` (speed 1.25), `Bruno` (speed 1.25), `Bella` (speed 1.25), `Luna` (speed 1.25).

Play each candidate sample aloud using the platform audio player (`(New-Object Media.SoundPlayer).PlaySync()` on Windows, `afplay` on macOS, `aplay` on Linux).

Ask the user which voice they prefer.

## Phase 5: Speech Preferences and Persona

Ask the user three concise configuration questions:

1. **Tone**:
   - `conversational` (friendly, first-person updates)
   - `formal` (neutral, concise third-person status reports)
   - `minimal` (under 5 words, e.g. "Build succeeded.")
2. **Frequency**:
   - `completions-and-errors` (recommended: notify only on completed tasks and failures)
   - `all-milestones` (notify at start, major steps, and completion)
   - `errors-only` (speak only when something breaks)
3. **Task categories to vocalize**:
   - Long builds and test suites
   - Code reviews
   - Research and diagnostic findings
   - Multi-agent swarm milestones

## Phase 6: Save Configuration

Write the resulting preferences to `./.speak.md` in the repository root (or `~/.config/speak/config.md` if the user requested global configuration):

```yaml
---
engine: pocket-tts
server_url: http://localhost:8000
voice: eponine
tone: conversational
frequency: completions-and-errors

tasks:
  builds_and_tests: true
  task_completion: true
  errors_and_crashes: true
  research_findings: true
  code_reviews: false

audio:
  volume: 1.5
  mode: safe
---

# Speak Configuration
Created by /setup-speak. Edit values directly or run /edit-speak to modify.
```

Close the session by confirming that speech is enabled and ready for the next task.
