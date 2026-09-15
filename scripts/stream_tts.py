#!/usr/bin/env python3
"""
stream_tts.py — Hybrid TTS player for pocket-tts.

Modes:
  auto     (default) — short texts use streaming, long texts use safe mode
  stream   — real-time streaming, lowest latency, may crackle if server is throttled
  safe     — download full audio first, then play; no crackling, ~1-2s extra delay

Usage:
    uv run --with sounddevice --with requests --with numpy stream_tts.py \
        "Your text here" [voice] [tts_url] [mode]

Modes: auto | stream | safe
"""

import struct
import sys
import threading
import queue
import numpy as np
import requests
import sounddevice as sd
import ctypes
import os
import json
import time
import subprocess
from datetime import datetime, timezone

HTTP_CHUNK_SIZE  = 8192
PRE_BUFFER_BYTES = 24000 * 2 * 1   # 1 second pre-buffer for stream mode
AUTO_MODE_THRESHOLD = 120           # characters; above this, use safe mode


def find_wav_chunk(buf: bytes, chunk_id: bytes):
    idx = buf.find(chunk_id)
    if idx == -1: return None, None
    if len(buf) < idx + 8: return None, None
    size = struct.unpack_from("<I", buf, idx + 4)[0]
    return idx + 8, size


def apply_volume(audio: np.ndarray, volume: float) -> np.ndarray:
    """Apply volume multiplier with tanh soft-clipping to prevent harsh distortion."""
    if volume == 1.0:
        return audio
    audio_f = audio.astype(np.float32) * volume
    peak = 32767.0
    mask = np.abs(audio_f) > peak
    if np.any(mask):
        audio_f[mask] = peak * np.tanh(audio_f[mask] / peak)
    return audio_f.astype(np.int16)


def play_safe_bytes(raw: bytes, volume=1.0):
    """Play full WAV audio bytes atomically — zero underruns."""
    if not raw:
        print("[stream_tts] ERROR: Empty audio payload.", file=sys.stderr)
        sys.exit(1)

    sample_rate = 24000
    data_offset, _ = find_wav_chunk(raw, b"data")
    if data_offset is None:
        print("[stream_tts] ERROR: No WAV data chunk.", file=sys.stderr)
        sys.exit(1)

    fmt_offset, _ = find_wav_chunk(raw, b"fmt ")
    if fmt_offset is not None and len(raw) >= fmt_offset + 8:
        sample_rate = struct.unpack_from("<I", raw, fmt_offset + 4)[0]

    pcm = raw[data_offset:]
    if len(pcm) % 2 != 0:
        pcm = pcm[:-1]

    audio = np.frombuffer(pcm, dtype=np.int16)
    audio = apply_volume(audio, volume)
    sd.play(audio, samplerate=sample_rate)
    sd.wait()


def play_safe(resp, volume=1.0) -> bytes:
    """Download full audio then play atomically — returns raw WAV bytes."""
    raw = b""
    for chunk in resp.iter_content(chunk_size=HTTP_CHUNK_SIZE):
        if chunk:
            raw += chunk

    play_safe_bytes(raw, volume=volume)
    return raw


def play_stream(resp, volume=1.0):
    """Real-time streaming with pre-buffer and silence-fill on underruns."""
    pcm_queue = queue.Queue()

    def downloader():
        http_buf = b""
        header_done = False
        try:
            for http_chunk in resp.iter_content(chunk_size=HTTP_CHUNK_SIZE):
                if not http_chunk: continue
                http_buf += http_chunk

                if not header_done:
                    if len(http_buf) < 44: continue
                    data_offset, _ = find_wav_chunk(http_buf, b"data")
                    if data_offset is None: continue
                    header_done = True
                    pcm = http_buf[data_offset:]
                    if pcm: pcm_queue.put(pcm)
                    http_buf = b""
                else:
                    pcm_queue.put(http_buf)
                    http_buf = b""
        except Exception as e:
            print(f"\n[stream_tts] Download error: {e}", file=sys.stderr)
        pcm_queue.put(None)

    dl_thread = threading.Thread(target=downloader, daemon=True)
    dl_thread.start()

    state = {"buffer": bytearray(), "finished": False}

    while True:
        chunk = pcm_queue.get()
        if chunk is None:
            state["finished"] = True
            break
        state["buffer"].extend(chunk)
        if len(state["buffer"]) >= PRE_BUFFER_BYTES:
            break

    def callback(outdata, frames, time, status):
        bytes_needed = frames * 2
        while not pcm_queue.empty():
            try:
                chunk = pcm_queue.get_nowait()
                if chunk is None:
                    state["finished"] = True
                else:
                    state["buffer"].extend(chunk)
            except queue.Empty:
                break

        avail = len(state["buffer"])
        if avail >= bytes_needed:
            data = state["buffer"][:bytes_needed]
            del state["buffer"][:bytes_needed]
            chunk_arr = np.frombuffer(bytes(data), dtype=np.int16)
            chunk_arr = apply_volume(chunk_arr, volume)
            outdata[:] = chunk_arr.reshape(-1, 1)
        else:
            usable = avail - (avail % 2)
            samples = 0
            if usable > 0:
                data = state["buffer"][:usable]
                del state["buffer"][:usable]
                samples = usable // 2
                chunk_arr = np.frombuffer(bytes(data), dtype=np.int16)
                chunk_arr = apply_volume(chunk_arr, volume)
                outdata[:samples] = chunk_arr.reshape(-1, 1)
            outdata[samples:] = 0
            if state["finished"] and len(state["buffer"]) < 2:
                raise sd.CallbackStop

    stream = sd.OutputStream(samplerate=24000, channels=1, dtype='int16', callback=callback, latency='high')
    with stream:
        while stream.active:
            sd.sleep(50)


def save_outfile(raw: bytes, outfile: str):
    """Save raw audio bytes to file path (.wav or .mp3)."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(outfile)), exist_ok=True)
        if outfile.lower().endswith(".mp3"):
            try:
                import lameenc
                data_offset, _ = find_wav_chunk(raw, b"data")
                pcm = raw[data_offset:] if data_offset else raw
                if len(pcm) % 2 != 0: pcm = pcm[:-1]
                encoder = lameenc.Encoder()
                encoder.set_bit_rate(128)
                encoder.set_in_sample_rate(24000)
                encoder.set_channels(1)
                encoder.set_quality(2)
                out_data = encoder.encode(pcm) + encoder.flush()
            except ImportError:
                print("[stream_tts] WARNING: lameenc not installed. Saving WAV data into .mp3 extension file.", file=sys.stderr)
                out_data = raw
            except Exception as e:
                print(f"[stream_tts] WARNING: MP3 encoding error ({e}). Saving RAW audio.", file=sys.stderr)
                out_data = raw
        else:
            out_data = raw

        with open(outfile, "wb") as f:
            f.write(out_data)
        print(f"[speak] Saved audio to {outfile}")
    except Exception as e:
        print(f"[speak] Error saving file: {e}", file=sys.stderr)


def atomic_write_json(filepath: str, data: dict):
    """Atomically write dictionary to JSON file via temporary replacement."""
    tmp_path = filepath + f".tmp.{os.getpid()}"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except OSError: pass


def acquire_lock_and_start_heartbeat(lock_file: str, agent_name: str) -> threading.Event:
    max_heartbeat_age = 12
    max_wait = 45
    retry_interval = 0.5
    deadline = time.time() + max_wait

    while True:
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)

                hb_str = lock_data.get("heartbeat", "")
                if hb_str:
                    hb_time = datetime.fromisoformat(hb_str.replace('Z', '+00:00'))
                    if hb_time.tzinfo is None:
                        hb_time = hb_time.replace(tzinfo=timezone.utc)
                    age = (datetime.now(timezone.utc) - hb_time).total_seconds()
                    if age <= max_heartbeat_age:
                        if time.time() > deadline:
                            sys.exit(0)
                        time.sleep(retry_interval)
                        continue
                    else:
                        # Lock is stale (>12s old), steal it cleanly
                        try: os.remove(lock_file)
                        except OSError: pass
            except (json.JSONDecodeError, OSError):
                # Transient file read/write lock contention — sleep & retry without deleting lock!
                time.sleep(retry_interval)
                continue
            except Exception:
                time.sleep(retry_interval)
                continue

        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({
                    "agent": agent_name,
                    "acquired_at": datetime.now(timezone.utc).isoformat(),
                    "heartbeat": datetime.now(timezone.utc).isoformat()
                }, f)
            break
        except FileExistsError:
            time.sleep(retry_interval)

    stop_event = threading.Event()
    def heartbeat():
        while not stop_event.is_set():
            time.sleep(5)
            if not os.path.exists(lock_file):
                break
            try:
                data = {
                    "agent": agent_name,
                    "acquired_at": datetime.now(timezone.utc).isoformat(),
                    "heartbeat": datetime.now(timezone.utc).isoformat()
                }
                atomic_write_json(lock_file, data)
            except Exception:
                break

    hb_thread = threading.Thread(target=heartbeat, daemon=True)
    hb_thread.start()
    return stop_event


def ensure_server_online(url: str) -> bool:
    """Check TTS server health; auto-start pocket-tts serve in background if offline."""
    health_url = url.replace("/tts", "/health")
    for attempt in range(3):
        try:
            resp = requests.get(health_url, timeout=2)
            if resp.status_code == 200:
                return True
        except Exception:
            pass

        if attempt == 0:
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                subprocess.Popen(["pocket-tts", "serve"], creationflags=creationflags)
                time.sleep(2)
            except Exception as e:
                print(f"[speak] Could not auto-start pocket-tts serve: {e}", file=sys.stderr)
                break
        else:
            time.sleep(1)

    return False


def main():
    if sys.platform == 'win32':
        try:
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
        except Exception:
            pass

    text  = os.environ.get("TTS_TEXT", sys.argv[1] if len(sys.argv) > 1 else "Hello")
    voice = os.environ.get("TTS_VOICE", sys.argv[2] if len(sys.argv) > 2 else "eponine")
    url   = os.environ.get("TTS_URL", sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000/tts")
    mode  = os.environ.get("TTS_MODE", sys.argv[4] if len(sys.argv) > 4 else "safe")

    agent = os.environ.get("TTS_AGENT", "agent")
    lock_file = os.environ.get("TTS_LOCKFILE", "")
    outfile = os.environ.get("TTS_OUTFILE", "")
    noplay  = os.environ.get("TTS_NOPLAY", "0") in ("1", "true", "True")

    try:
        volume = float(os.environ.get("TTS_VOLUME", "1.0"))
    except ValueError:
        volume = 1.0

    # Ensure server is online or auto-started
    if not ensure_server_online(url):
        print("[speak] TTS SERVER OFFLINE - Cannot speak.", file=sys.stderr)
        sys.exit(0)

    # Fast path for silent generation (NoPlay)
    if noplay:
        if outfile:
            try:
                resp = requests.post(url, data={"text": text, "voice_url": voice}, timeout=60)
                resp.raise_for_status()
                save_outfile(resp.content, outfile)
            except Exception as e:
                print(f"[speak] Error generating silent audio: {e}", file=sys.stderr)
                sys.exit(1)
        sys.exit(0)

    stop_event = None
    if lock_file:
        stop_event = acquire_lock_and_start_heartbeat(lock_file, agent)

    if mode == "auto":
        mode = "safe" if len(text) > AUTO_MODE_THRESHOLD else "stream"

    try:
        resp = requests.post(
            url,
            data={"text": text, "voice_url": voice},
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[speak] Error requesting speech from server: {e}", file=sys.stderr)
        if stop_event:
            stop_event.set()
            try: os.remove(lock_file)
            except OSError: pass
        sys.exit(1)

    raw_audio = None
    if mode == "safe":
        raw_audio = play_safe(resp, volume=volume)
    else:
        play_stream(resp, volume=volume)

    # If OutFile was specified, save audio to disk even when playback was active
    if outfile:
        if raw_audio is None:
            # For stream mode, re-fetch or read raw payload if needed
            try:
                r2 = requests.post(url, data={"text": text, "voice_url": voice}, timeout=60)
                if r2.status_code == 200:
                    raw_audio = r2.content
            except Exception:
                pass
        if raw_audio:
            save_outfile(raw_audio, outfile)

    if stop_event:
        stop_event.set()
        try: os.remove(lock_file)
        except OSError: pass

if __name__ == "__main__":
    main()

