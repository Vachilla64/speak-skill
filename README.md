# 🎙️ speak-skill

> **Because Audio is just more natural.**  
> Built for Claude Code, Cursor, Antigravity, and autonomous agent swarms.

`speak-skill` gives your AI agents an ambient voice, running **100% offline on your CPU**.

You have to experience it to understand the value — give it a try!

Agents can vocalize milestone updates, completion alerts, questions, plans, and build errors without you needing to stare at terminal logs.

A big thanks to the open-source creators:
- **[Kyutai Labs](https://kyutai.org)** ([GitHub](https://github.com/kyutai-labs/pocket-tts)) — Pocket-TTS and Mimi audio codec.
- **[hexgrad](https://github.com/hexgrad/kokoro)** ([Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)) — Kokoro-82M.
- **[KittenML](https://kittenml.com)** ([GitHub](https://github.com/KittenML/KittenTTS)) — Kitten TTS.

---

## ⚡ Real-World Benchmarks & Hardware Reality

Measured on an **Intel Core i3-10110U (2 cores, 4 threads @ 2.10 GHz), 8 GB total RAM, Windows 11 Home** under battery power / power efficiency mode, with typical developer background apps running (IDE, local LLMs, browser):

| Engine | Model Weights | Free RAM Required | Real-World Generation Time (15-word phrase) | Audio Output | What to Expect |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Pocket-TTS** (Kyutai) | ~150 MB | **~1.5 GB – 2.0 GB** | **~12s – 18s** (on a dual-core i3 under memory load) | 24 kHz mono | **Top Quality & Personality**: Rich conversational inflections, zero-shot voice cloning. Requires CPU headroom for real-time speed. |
| **Kokoro-82M** (hexgrad) | ~82 MB | **~800 MB – 1.2 GB** | **~4s – 8s** | 24 kHz mono | **Studio Fidelity**: 54+ voices across 8 languages. Fast on CPU, high consistency. |
| **Kitten TTS** (KittenML) | **< 25 MB** | **~300 MB – 500 MB** | **~1.3s – 2.5s** | 24 kHz mono | **Lightweight Champion**: Runs via pure ONNX. Set `speed=1.25` for natural human speaking rate. |

> **Honest Engineering Note**: On high-spec machines (Apple M-series or modern 8+ core AMD/Intel chips), Pocket-TTS runs at **4x–8x real-time** (sub-second synthesis). On entry-level dual-core laptops with constrained RAM (<1 GB free), heavy PyTorch engines like Pocket-TTS slow down, whereas lightweight ONNX models (Kitten TTS) remain snappy.

---

## 💾 Model Storage & Where Files Live

All speech synthesis models run 100% locally on your machine. No telemetry or audio ever leaves your system.

### 1. Default Download Directories
By default, the Python and Hugging Face ecosystems cache downloaded model weights to standard user cache folders:

- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **macOS / Linux**: `~/.cache/huggingface/hub/`

### 2. Customizing Storage Location
If you want to store weights on an external drive or custom folder, set the standard environment variable before running your TTS server or agent:

```bash
# Windows (PowerShell)
$env:HF_HOME = "D:\AI_Models\huggingface"

# macOS / Linux (Bash/Zsh)
export HF_HOME="/Volumes/ExternalSSD/AI_Models/huggingface"
```

### 3. How to Completely Remove All Downloaded Models
If you want to clean up disk space or remove all models:
```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--kyutai*"
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--hexgrad*"
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--KittenML*"

# macOS / Linux
rm -rf ~/.cache/huggingface/hub/models--kyutai*
rm -rf ~/.cache/huggingface/hub/models--hexgrad*
rm -rf ~/.cache/huggingface/hub/models--KittenML*
```

---

## 📦 Installation

Install directly into your agent harness using `npx skills` (recommended):

```bash
npx skills add Vachilla64/speak-skill
```

Or clone into your local skill directory:

```bash
git clone https://github.com/Vachilla64/speak-skill.git ~/.claude/skills/speak-skill
```

---

## 🚀 Quickstart & How It Works

Once installed, there is **zero complex setup**. You don't need a manual:

### 1. Start Your Local TTS Server
Run your favorite engine in the background:
```bash
# Pocket-TTS (Kyutai) — instant launch via uvx
uvx pocket-tts serve
```

### 2. Just Tell Your Agent What You Like
Use `/edit-speak` or simply tell your agent directly in conversation:
> *"Hey, speak to me in a formal tone only when builds fail."*  
> *"Switch your voice to Michael and keep messages minimal."*  
> *"Only notify me on completed test runs."*

The `/edit-speak` skill handles updating `.speak.md` automatically behind the scenes:
- **Tone**: `conversational` | `formal` | `minimal`
- **Frequency**: `completions-and-errors` | `all-milestones` | `errors-only` | `silent`
- **Voice**: Pick any voice from your running engine (`eponine`, `michael`, `Jasper`, `af_heart`)

### 3. Automatic Ambient Vocalization
Once configured, the agent reaches for `speak` in the background without blocking its work:
```text
Agent: "Build complete. All unit tests passed, ready to ship."
```

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
│   ├── speak.sh           # Unix/macOS launcher with auto-start & background detachment
│   └── stream_tts.py      # Python streaming player with heartbeat lease management
├── README.md
└── LICENSE
```

---

## 📄 License

MIT License. Crafted with ❤️ by [Alfred Valentine](https://github.com/Vachilla64).
