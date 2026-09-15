<#
.SYNOPSIS
    Streams and plays TTS audio from pocket-tts in real-time, with a
    distributed heartbeat lock to prevent multiple agents speaking at once.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Text,

    [string]$Voice = "eponine",

    [string]$TtsUrl = "http://localhost:8000/tts",

    [string]$Mode = "safe",

    [string]$AgentName = "",

    [string]$Volume = "1.5",

    [string]$OutFile = "",

    [switch]$NoPlay
)

$ErrorActionPreference = "SilentlyContinue"
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$playerScript = Join-Path $scriptDir "stream_tts.py"
$lockFile     = Join-Path $scriptDir "speak.lock"

if (-not (Test-Path $playerScript)) {
    exit 0
}

# ── Speak ─────────────────────────────────────────────────────────────────────
try {
    $env:OPENBLAS_NUM_THREADS = "1"
    $env:GOTO_NUM_THREADS     = "1"
    $env:OMP_NUM_THREADS      = "1"

    # Health check & auto-start server if offline
    $healthUrl = $TtsUrl.Replace("/tts", "/health")
    $isOnline = $false
    try {
        $resp = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($resp -and $resp.status -eq "healthy") { $isOnline = $true }
    } catch {}

    if (-not $isOnline) {
        if (Get-Command "pocket-tts" -ErrorAction SilentlyContinue) {
            Start-Process -FilePath "pocket-tts" -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 2
        } elseif (Get-Command "uvx" -ErrorAction SilentlyContinue) {
            Start-Process -FilePath "uvx" -ArgumentList "pocket-tts", "serve" -WindowStyle Hidden
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

    $needsLameenc = $OutFile -and $OutFile.ToLower().EndsWith(".mp3")

    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        if ($needsLameenc) {
            uv run --with sounddevice --with requests --with numpy --with lameenc $playerScript
        } else {
            uv run --with sounddevice --with requests --with numpy $playerScript
        }
    } else {
        python $playerScript
    }
} catch {
    exit 0
}
