---
name: speak
description: Give the agent a voice to notify the user of progress, completion, findings, or errors. Reached when the agent wants to speak aloud or the user asks for audio feedback.
---

Give the agent a voice using a local neural text-to-speech engine.

## Core Rule: Never Block on Audio

Audio playback takes real-world seconds. Never run speech synchronously or wait for playback to complete before continuing your work.

Always fire speech as a background process (WaitMsBeforeAsync: 500 or background shell job) so you can proceed to your next tool call immediately.

## When to Speak

- **Task start**: One sentence confirming what you are starting.
- **Milestones**: When finishing a major step during a long task.
- **Completion**: Clear summary of what was accomplished and verified.
- **Errors**: Immediate audible notification if a build, test, or process fails.
- **Key findings**: Verbal summary when research or diagnosis yields a crucial discovery.

Keep messages short (1 to 2 sentences). Avoid reading raw code blocks, file diffs, or terminal stack traces out loud. Summarize the intent in plain language.

## Reading Configuration

Before speaking, check for configuration in this order:

1. `./.speak.md` (repo-local configuration)
2. `~/.config/speak/config.md` (user-global configuration)
3. Hardcoded default fallback: Pocket-TTS at `http://localhost:8000/tts`, voice `eponine`, tone `conversational`.

If the active configuration has `frequency: silent` or disables notifications for the current task category, skip speaking and proceed silently.

## How to Call the Active Engine

Run the platform driver script in the background to handle auto-starting, volume soft-clipping, and multi-agent heartbeat locking automatically:

### 1. Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File "scripts/speak.ps1" -Text "Task completed successfully."
```

### 2. macOS / Linux (Bash)

```bash
bash scripts/speak.sh "Task completed successfully."
```

### 3. Direct HTTP Fallback (When scripts are not in workspace)

```bash
# Pocket-TTS (localhost:8000)
curl -s -X POST "http://localhost:8000/tts" -d "text=Task completed successfully." -d "voice_url=eponine" -o /tmp/tts.wav && (afplay /tmp/tts.wav || aplay /tmp/tts.wav || ffplay -nodisp -autoexit /tmp/tts.wav) >/dev/null 2>&1 &

# Kokoro-FastAPI (localhost:8880)
curl -s -X POST "http://localhost:8880/v1/audio/speech" -H "Content-Type: application/json" -d '{"model":"kokoro","input":"Task completed successfully.","voice":"af_heart"}' -o /tmp/tts.mp3 && (afplay /tmp/tts.mp3 || mpg123 /tmp/tts.mp3 || ffplay -nodisp -autoexit /tmp/tts.mp3) >/dev/null 2>&1 &
```

## Concurrency Lock

In multi-agent swarms, multiple agents can finish tasks simultaneously. The driver scripts automatically manage a heartbeat lock (`speak.lock`) with active lease renewal and stale steal protection to prevent overlapping speech.

## Graceful Degradation

If the TTS server is unreachable (connection refused) or an audio device is unavailable, the driver fails silently with exit code 0. Never allow audio generation errors to break your primary engineering objective.
