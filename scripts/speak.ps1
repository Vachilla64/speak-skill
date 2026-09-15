<#
.SYNOPSIS
    Streams and plays TTS audio from pocket-tts in real-time, with a
    distributed heartbeat lock to prevent multiple agents speaking at once.

.DESCRIPTION
    Invokes stream_tts.py via uv, passing arguments via environment variables.
    The python script handles its own file locking, background heartbeat thread,
    and graceful fallback if the server is offline.

.PARAMETER Text
    The text to convert to speech. Required.

.PARAMETER Voice
    Built-in voice name (e.g. "eponine") or a voice URL. Defaults to "eponine".

.PARAMETER TtsUrl
    Full URL of the pocket-tts TTS endpoint. Defaults to http://localhost:8000/tts.

.PARAMETER Mode
    Playback mode: stream | safe.
    stream = real-time streaming, lowest latency
    safe   = download full audio then play, crackle-free but ~1-2s extra delay (default)

.PARAMETER AgentName
    Optional. Name of the calling agent (e.g. "builder", "researcher").

.PARAMETER Volume
    Audio volume multiplier. Defaults to 1.5 (boosted).

.PARAMETER OutFile
    Optional file path (.wav or .mp3) to save generated audio to.

.PARAMETER NoPlay
    If specified, suppresses audio playback (only saves to OutFile if provided).
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Text,

    [string]$Voice = "michael",

    [string]$TtsUrl = "http://localhost:8000/tts",

    [string]$Mode = "safe",

    [string]$AgentName = "",

    [string]$Volume = "1.5",

    [string]$OutFile = "",

    [switch]$NoPlay
)

$ErrorActionPreference = "Stop"
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$playerScript = Join-Path $scriptDir "stream_tts.py"
$lockFile     = Join-Path $scriptDir "speak.lock"

if (-not (Test-Path $playerScript)) {
    Write-Error "[speak] stream_tts.py not found at: $playerScript"
    exit 1
}

# ── Speak ─────────────────────────────────────────────────────────────────────
try {
    # Prevent OpenBLAS from spinning up parallel threads (causes memory errors on Windows)
    $env:OPENBLAS_NUM_THREADS = "1"
    $env:GOTO_NUM_THREADS     = "1"
    $env:OMP_NUM_THREADS      = "1"

    # Health check & server auto-start using pocket-tts directly (no uvx)
    $healthUrl = $TtsUrl.Replace("/tts", "/health")
    $isOnline = $false
    try {
        $resp = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($resp -and $resp.status -eq "healthy") { $isOnline = $true }
    } catch {}

    if (-not $isOnline) {
        if (Get-Command "pocket-tts" -ErrorAction SilentlyContinue) {
            Start-Process -FilePath "pocket-tts" -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 2
        }
    }

    $env:TTS_TEXT     = $Text
    $env:TTS_VOICE    = $Voice
    $env:TTS_URL      = $TtsUrl
    $env:TTS_MODE     = $Mode
    $env:TTS_AGENT    = $AgentName
    $env:TTS_LOCKFILE = $lockFile
    $env:TTS_VOLUME   = $Volume
    $env:TTS_OUTFILE  = $OutFile
    $env:TTS_NOPLAY   = if ($NoPlay) { "1" } else { "0" }

    # lameenc is only required when saving to an .mp3 file — skip it for normal playback
    # to avoid PyPI network fetch on every TTS call
    $needsLameenc = $OutFile -and $OutFile.ToLower().EndsWith(".mp3")

    if ($needsLameenc) {
        uv run `
            --with sounddevice `
            --with requests `
            --with numpy `
            --with lameenc `
            $playerScript
    } else {
        uv run `
            --with sounddevice `
            --with requests `
            --with numpy `
            $playerScript
    }
} catch {
    Write-Error $_
}

