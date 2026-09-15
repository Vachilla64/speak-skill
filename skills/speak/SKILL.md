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

### 1. Pocket-TTS (Default, localhost:8000)

```powershell
# Windows (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/tts" -Method Post -Body @{ text = "Task completed successfully."; voice_url = "eponine" } -OutFile "$env:TEMP\tts.wav"; Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -Command `"(New-Object Media.SoundPlayer '$env:TEMP\tts.wav').PlaySync()`"" -WindowStyle Hidden
```

```bash
# macOS / Linux
curl -s -X POST "http://localhost:8000/tts" -d "text=Task completed successfully." -d "voice_url=eponine" -o /tmp/tts.wav && (afplay /tmp/tts.wav || aplay /tmp/tts.wav || ffplay -nodisp -autoexit /tmp/tts.wav) >/dev/null 2>&1 &
```

### 2. Kokoro-FastAPI (localhost:8880)

```bash
curl -s -X POST "http://localhost:8880/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"model":"kokoro","input":"Task completed successfully.","voice":"af_heart"}' \
  -o /tmp/tts.mp3 && (afplay /tmp/tts.mp3 || mpg123 /tmp/tts.mp3 || ffplay -nodisp -autoexit /tmp/tts.mp3) >/dev/null 2>&1 &
```

### 3. Kitten TTS (Pure ONNX, lightweight)

```bash
python -c "from kittentts import KittenTTS; m = KittenTTS('KittenML/kitten-tts-nano-0.8'); m.generate_to_file('Task completed successfully.', '/tmp/tts.wav', voice='Jasper', speed=1.25)" && (afplay /tmp/tts.wav || aplay /tmp/tts.wav) >/dev/null 2>&1 &
```

## Concurrency Lock

In multi-agent swarms, multiple agents can finish tasks simultaneously. Always inspect the local lock file before speaking:

- Lock file path: `./.speak.lock` (or `$TEMP/speak.lock`).
- If a lock exists and its timestamp is less than 10 seconds old, wait or queue your message.
- If the lock is older than 10 seconds (stale from a crashed process), overwrite it with your own process ID and timestamp.
- Delete the lock file once playback begins or ends.

## Graceful Degradation

If the TTS server is unreachable (connection refused) or an audio device is unavailable, catch the error and fail silently. Never allow audio generation errors to break your primary engineering objective.
