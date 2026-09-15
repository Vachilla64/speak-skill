# 🎙️ speak-skill

> **Because Audio is just more natural.**  
> Built for Claude Code, Cursor, Antigravity, and autonomous agent swarms.

`speak-skill` gives your AI agents an ambient voice, running **100% offline on your CPU**.

You have to experience it to understand the value — give it a try!

Agents can vocalize milestone updates, completion alerts, questions, plans, and build errors without you needing to stare at terminal logs.

A big thanks to the engineers and researchers behind the open-weight engines that power this:
- **[Kyutai Labs](https://kyutai.org)** ([GitHub](https://github.com/kyutai-labs/pocket-tts)) — creators of Pocket-TTS and the Mimi audio codec.
- **[hexgrad](https://github.com/hexgrad/kokoro)** ([Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)) — creators of Kokoro-82M.
- **[KittenML](https://kittenml.com)** ([GitHub](https://github.com/KittenML/KittenTTS)) — creators of Kitten TTS.

This skill is open to contributions with your favorite TTS engines. I personally really love the Kyutai voices!

---

## ⚡ Benchmarks

Tested locally on consumer laptop hardware under active battery power:
- **System Specs**: Intel Core i3-10110U (2 cores, 4 threads @ 2.10 GHz), 8 GB RAM, Windows 11 Home.
- **Operating Mode**: Windows Power Saver / Best Power Efficiency (no discrete GPU, CPU-only).

| Engine | Model Size | Working RAM | RTF (Real-Time Factor) | Speed (CPU) | Audio Specs | Ideal Use Case |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pocket-TTS** (Kyutai) | ~150 MB | ~300 MiB | **0.15 – 0.22** | 4x–7x real-time | 24 kHz mono | **Top Pick**: Rich conversational cadence, zero-shot voice cloning. |
| **Kokoro-82M** (hexgrad) | ~82 MB | ~150 MiB | **0.18 – 0.30** | 3x–6x real-time | 24 kHz mono | **Studio Fidelity**: 54+ voices across 8 languages. |
| **Kitten TTS** (KittenML) | **< 25 MB** | **~30 MiB** | **0.17 – 0.20** | 5x–6x real-time | 24 kHz mono | **Minimal Footprint**: Runs in pure ONNX, sub-35 MB RAM. |

*Note: In Kitten TTS, an internal speed prior multiplier of 0.8 is applied by default in model weights. Set `speed=1.25` for natural human speaking rate.*

---

## ✨ Features

- **⚡ It's Asynchronous!**: Audio synthesis and playback run asynchronously in the background (`WaitMsBeforeAsync: 500`). The agent immediately moves on to its next tool call without waiting for audio to finish playing.
- **🔒 Multi-Agent Speech Handling**: Built-in PID/file-lease concurrency lock (`speak.lock`) prevents multiple agents in a swarm from talking over one another.
- **🎧 High-Fidelity Local TTS**: Zero cloud API keys, zero external network calls during synthesis:
  - **[Pocket-TTS](https://kyutai.org)** ([GitHub](https://github.com/kyutai-labs/pocket-tts)): 100M parameters, CPU-first, natural conversational inflection, and zero-shot voice cloning from a 5-second audio sample.
  - **[Kokoro-82M](https://github.com/hexgrad/kokoro)** ([Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)): 82M parameters, 54+ studio voices across 8 languages.
  - **[Kitten TTS](https://kittenml.com)** ([GitHub](https://github.com/KittenML/KittenTTS)): Ultra-lightweight ONNX runtime under 25 MB on disk, running in ~30 MiB RAM.

---

## 📦 Installation & Setup Guide

### 1. Install the Skill
Install directly into your agent harness using `npx skills` (recommended):

```bash
npx skills add Vachilla64/speak-skill
```

Or clone into your local agent skills directory:

```bash
# Claude Code / Codex / Antigravity
git clone https://github.com/Vachilla64/speak-skill.git ~/.claude/skills/speak-skill
```

### 2. The 3-Skill Modular Suite
Once installed, your agent has access to 3 specialized skills:
- **`/setup-speak`** — Interactive setup wizard: detects your OS, starts your local engine daemon, plays live voice auditions, and configures preferences.
- **`speak`** — The main lean execution contract the agent calls automatically whenever it wants to tell you something.
- **`/edit-speak`** — Quick settings modifier for voice, tone, frequency, and volume.

---

## 🚀 Quickstart

Because these are local AI models, they run 100% on your system.
- **Model Storage**: Model weights are downloaded automatically on first launch and cached locally (e.g. `~/.cache/huggingface/hub`). They take between 25 MB (Kitten) and 200 MB (Pocket-TTS) of disk space. No cloud connection is used once downloaded.

### Step 1: Run the Setup Wizard
Inside your coding agent session, type:
```text
/setup-speak
```
The wizard will:
1. Detect your host operating system (Windows, macOS, Linux).
2. Guide you through launching your preferred local engine (e.g. `uvx pocket-tts serve`).
3. **Audition candidate voices aloud** through your speakers so you hear each voice before choosing.
4. Let you configure persona tone and notification frequency.
5. Save your preferences to `.speak.md` in your project root or `~/.config/speak/config.md` globally.

### Step 2: Automatic Vocalization
Once configured, the agent reaches for `speak` automatically when completing tasks, reporting findings, or hitting errors:
```text
Agent: "Build complete. All 42 unit tests passed, ready to ship."
```

---

## 🎭 Personality and Customization

Different LLMs have distinct communication styles and personalities:
- **Gemini** tends to be communicative and detailed.
- **OpenAI** models are conversational and chatty.
- **Anthropic** models are often more reserved and concise.

Your experience may vary depending on prompt and model, but you can tailor how your agent speaks using `/setup-speak` or `/edit-speak`:

### 1. Tone Profiles
- **`conversational`** (default): Friendly, first-person spoken updates (e.g. *"I've refactored the database schema, running the migration suite now."*).
- **`formal`**: Objective, third-person status reports (e.g. *"Database schema refactoring complete. Executing migrations."*).
- **`minimal`**: Clipped status notices under five words for minimal distraction (e.g. *"Migrations passed."*).

### 2. Frequency Control
- **`completions-and-errors`** (recommended): The agent only speaks when a task succeeds or when something breaks.
- **`all-milestones`**: Speaks at task start, major intermediate checkpoints, and completion.
- **`errors-only`**: Silent workhorse mode — only speaks up if a build, test, or script fails.
- **`silent`**: Mutes voice output temporarily without uninstalling your setup.

### 3. Task Filters
Choose which specific tasks warrant voice notifications:
- Builds and unit test suites
- Code reviews and audits
- Research and diagnostic findings
- Multi-agent swarm milestones

All settings are stored in `.speak.md` and can be adjusted at any time with `/edit-speak`.

---

## 📂 Repository Structure

```
speak-skill/
├── skills/
│   ├── speak/             # Lean model-invoked runtime contract
│   │   └── SKILL.md
│   ├── setup-speak/       # Interactive setup wizard with live voice auditions
│   │   └── SKILL.md
│   └── edit-speak/        # Fast configuration & tone updater
│       └── SKILL.md
├── scripts/
│   ├── speak.ps1          # Cross-process PowerShell audio launcher & lock manager
│   └── stream_tts.py      # Python streaming player with heartbeat lease management
├── README.md
└── LICENSE
```

---

## 🤝 Contribution and Feedback

Pull requests and community contributions are very welcome!
Whether it's adding new local TTS engine backends, custom language packs, or integrations with other agent frameworks:
- Check out `skills/setup-speak/SKILL.md` to see how engine options are registered.
- Feel free to submit PRs or open issues with your feedback and voice suggestions.

This skill was originally built for personal daily engineering use, but it proved so essential to flow and focus that I had to share it.

A special thank you again to the researchers and open-source teams at **Kyutai Labs**, **hexgrad**, and **KittenML** for making high-quality, local, open-weight speech synthesis accessible on consumer hardware.

---

## 📄 License

MIT License. Crafted with ❤️ by [Alfred Valentine](https://github.com/Vachilla64).
