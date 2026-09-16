# 🎙️ speak-skill

> **Because Voice, is just more natural.**  
> Built for Claude Code, Cursor, Antigravity, and autonomous agent swarms.

`speak-skill` gives your AI agents a voice! running 100% offline on your CPU.

Agents can vocalize milestone updates, completion alerts, questions, plans, and build errors without you needing to stare at terminal logs.

You have to experience it to understand the value — give it a try!

A big thanks to the open-source creators:
- **[Kyutai Labs](https://kyutai.org)** ([GitHub](https://github.com/kyutai-labs/pocket-tts)) — Pocket-TTS and Mimi audio codec.
- **[hexgrad](https://github.com/hexgrad/kokoro)** ([Official Demo](https://hf.co/spaces/hexgrad/Kokoro-TTS) • [Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)) — Kokoro-82M.
- **[KittenML](https://kittenml.com)** ([GitHub](https://github.com/KittenML/KittenTTS) • [Web Demo](https://huggingface.co/spaces/KittenML/KittenTTS)) — Kitten TTS.

---

## 📦 Installation

Install directly into your agent harness using `npx skills` (I recommend this):

```bash
npx skills add Vachilla64/speak-skill
```

Or clone into your local skill directory:

```bash
git clone https://github.com/Vachilla64/speak-skill.git ~/.claude/skills/speak-skill
```

---

## Quickstart & How It Works

Once installed, `speak-skill` is completely **plug-and-play**. You don't need to manually manage background terminals or start servers by hand.

### 1. Run the One-Time Setup Wizard
Run `/setup-speak` in your agent harness:
```text
/setup-speak
```
The wizard handles the initial engine download, plays live voice auditions directly through your speakers, and saves your preferred persona to `./.speak.md`.

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
Once configured, your agent reaches for `speak` in the background without blocking its work:
```text
Agent: "Build complete. All unit tests passed, ready to ship."
```

> **Self-Healing Server**: When your agent needs to speak, the background driver automatically checks server health (`/health`) and boots the engine if it's offline. If an issue occurs after setup was completed, the agent alerts you with quick troubleshooting steps.

<details>
<summary><b>🛠️ Manual Server Management (Optional)</b></summary>

If you prefer to run and monitor your TTS server in a dedicated terminal window:

- **Pocket-TTS (Kyutai)** (Permanent install, zero re-downloads):
  ```bash
  uv tool install pocket-tts
  pocket-tts serve
  ```
- **Kokoro-82M (hexgrad)** (Persistent model & voice volume caching):
  ```bash
  docker run -d --name kokoro-tts -p 8880:8880 \
    -v kokoro-models:/app/api/src/models \
    -v kokoro-voices:/app/api/src/voices \
    --restart unless-stopped \
    ghcr.io/remsky/kokoro-fastapi-cpu:latest
  ```
- **Kitten TTS (KittenML)**:
  Runs directly in-process via ONNX (`pip install kittentts soundfile onnxruntime`), or run a standalone server wrapper.
</details>

---

## 🔌 Dependencies & System Requirements

`speak-skill` is engineered to be **lightweight, offline, and non-intrusive**. It runs on bare-metal CPUs without requiring cloud accounts, external API keys, or telemetry.

### Minimal Host Prerequisite

To keep your system clean and avoid dependency conflicts, the only recommended tool is **`uv`**:

* **[uv](https://astral.sh/uv)** (Fast Python package and tool runner):
  * Single static binary with zero runtime overhead.
  * Runs tools in isolated environments without polluting system Python (`uv run`, `uv tool install`).
  * **Automatic Python Management**: If Python is not installed on your system, `uv` automatically downloads and manages a standalone Python build for you.

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### Engine Comparison Matrix

Choose the engine that matches your available hardware and preferred setup:

| Engine | Model Size | Runtime Engine | PyTorch Needed? | Docker Needed? | Peak RAM | Audio Quality & Cadence |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Kitten TTS** (KittenML) | **< 25 MB** | Pure ONNX | **No** | **No** | **~300 MB** | Snappy, clear, ultra-fast generation (3x real-time) |
| **Kokoro-82M** (`kokoro-onnx`) | 82 MB | Pure ONNX | **No** | **No** | ~300 MB | High prosody, studio-grade voices across 8 languages |
| **Kokoro-82M** (Docker) | 82 MB | Containerized API | Bundled | **Yes** | ~1.5 GB (+ Docker VM) | Fully isolated, OpenAI-compatible HTTP endpoint |
| **Pocket-TTS** (Kyutai) | 150 MB | PyTorch (CPU) | **Yes** | **No** | ~1.8 GB | Rich conversational cadence, breathing, voice cloning |

---

### Engine-by-Engine Breakdown

#### 1. Kitten TTS (KittenML): The Zero-Overhead Champion
* **Requirements**: Python 3.8+, `onnxruntime`, `soundfile`, `kittentts`.
* **No Docker, No PyTorch**: Runs entirely via ONNX Runtime.
* **Disk footprint**: Less than 25 MB for model weights.
* **Best for**: Laptops, resource-constrained environments, or developers who want instant voice with minimal resource usage.

```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl soundfile onnxruntime
```

#### 2. Kokoro-82M (hexgrad): Studio Quality
You have two ways to run Kokoro depending on whether you use Docker:

* **Option A: Pure ONNX (`kokoro-onnx`) (No Docker, No PyTorch)**  
  Run Kokoro locally using ONNX Runtime with zero Docker overhead:
  ```bash
  pip install kokoro-onnx soundfile
  ```
  *Requires `espeak-ng` for text-to-phoneme conversion:*
  * macOS: `brew install espeak-ng`
  * Linux: `sudo apt install espeak-ng`
  * Windows: `winget install eSpeak-NG.eSpeak-NG`

* **Option B: Containerized Server (`kokoro-fastapi`) (Docker)**  
  If you already run Docker Desktop, use the pre-packaged container. It bundles `espeak-ng` and all phonemizers inside the image:
  ```bash
  docker run -d --name kokoro-tts -p 8880:8880 \
    -v kokoro-models:/app/api/src/models \
    -v kokoro-voices:/app/api/src/voices \
    --restart unless-stopped \
    ghcr.io/remsky/kokoro-fastapi-cpu:latest
  ```

#### 3. Pocket-TTS (Kyutai Labs): Conversational Identity
* **Requirements**: Python 3.10+, PyTorch 2.5+ (CPU build).
* **No Docker Required**: Runs directly on bare metal.
* **Zero Re-Downloads**: Install once permanently with `uv tool install pocket-tts` so the binary stays on PATH.
* **Disk footprint**: ~150 MB model weights + ~800 MB PyTorch CPU cache.
* **Best for**: Developers who want natural conversational tone, subtle breathing cues, or custom voice cloning from a 5-second audio snippet.

```bash
# Permanent local installation with dedicated PATH binary
uv tool install pocket-tts

# Start server
pocket-tts serve
```

---

### Platform Audio Driver Notes

`speak-skill` routes synthesized audio to your default output device using lightweight native audio drivers:

* **Windows**:
  * Python `sounddevice` wheels automatically bundle PortAudio DLLs. No MSVC tools or C++ build chains are required.
  * Native fallback: PowerShell `System.Media.SoundPlayer` provides zero-dependency WAV playback.
* **macOS**:
  * Native player: `/usr/bin/afplay` is built into macOS. Zero external packages or Homebrew libraries required.
  * Python `sounddevice` wheel bundles PortAudio dylibs.
* **Linux**:
  * Native players: `aplay` (ALSA), `pw-play` (PipeWire), and `paplay` (PulseAudio) work out of the box.
  * If using Python streaming via `sounddevice`, install the system PortAudio library:
    ```bash
    # Ubuntu / Debian
    sudo apt install libportaudio2

    # Fedora
    sudo dnf install portaudio

    # Arch Linux
    sudo pacman -S portaudio
    ```

---

### How to Choose Your Setup

* **"I don't have Docker and don't want to install it":**  
  Use **Kitten TTS** or **Pocket-TTS** (`uv tool install pocket-tts`). Both run directly on your host machine without containers.
* **"I want the absolute smallest download and lowest RAM usage":**  
  Use **Kitten TTS**. The model is under 25 MB and uses approximately 300 MB of RAM.
* **"I want studio-quality voices without running Docker":**  
  Use **`kokoro-onnx`** with your system `espeak-ng` package.
* **"I want lifelike conversational flow and voice cloning":**  
  Use **Pocket-TTS**.
* **"I already have Docker running for my dev stack":**  
  Use the **`kokoro-fastapi-cpu`** container for an instant, self-contained OpenAI-compatible TTS server.

---

## Benchmarks

Measured on my **Intel Core i3-10110U (2 cores, 4 threads @ 2.10 GHz), 8 GB total RAM, Windows 11 Home** under battery power / power efficiency mode, with typical developer background apps running (IDE, local LLMs, browser):

| Engine | Model Size | Free RAM Needed | Generation Time (15 words) | What to Expect |
| :--- | :---: | :---: | :---: | :--- |
| **Pocket-TTS** (Kyutai) | ~150 MB | ~1.5 GB – 2.0 GB | ~12s – 18s | **Top Quality & Personality**: Rich conversational tone, voice cloning. Needs CPU headroom. |
| **Kokoro-82M** (hexgrad) | ~82 MB | ~800 MB – 1.2 GB | ~4s – 8s | **Studio Fidelity**: 54+ voices across 8 languages. Consistent, clean prosody. |
| **Kitten TTS** (KittenML) | **< 25 MB** | **~300 MB – 500 MB** | **~1.3s – 2.5s** | **Lightweight Champion**: Runs via pure ONNX. Ultra-fast and snappy on low-spec CPUs. |

*(All engines output 24 kHz mono audio locally.)*

---

## Model Storage 

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
