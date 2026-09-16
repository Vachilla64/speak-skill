import time
import requests
import soundfile as sf
import os

test_phrase = "I am your coding agent. All unit tests have passed, and your application is ready to ship."

print("=== 1. TESTING POCKET-TTS (localhost:8000) ===")
# Warm-up call
try:
    requests.post("http://localhost:8000/tts", data={"text": "Warm up.", "voice_url": "eponine"}, timeout=10)
except Exception as e:
    print(f"Pocket-TTS warm-up failed: {e}")

# Timed runs (average of 3 runs)
pocket_times = []
for i in range(3):
    t0 = time.time()
    resp = requests.post("http://localhost:8000/tts", data={"text": test_phrase, "voice_url": "eponine"}, timeout=30)
    gen_time = time.time() - t0
    pocket_times.append(gen_time)
    with open(f"bench_pocket_{i}.wav", "wb") as f:
        f.write(resp.content)

audio_data, sr = sf.read("bench_pocket_0.wav")
duration = len(audio_data) / float(sr)
avg_gen = sum(pocket_times) / len(pocket_times)
rtf = avg_gen / duration
speed_mult = duration / avg_gen
print(f"Pocket-TTS (eponine): Duration: {duration:.2f}s | Gen Time: {avg_gen:.2f}s | RTF: {rtf:.2f} | Speed: {speed_mult:.2f}x real-time")

print("\n=== 2. TESTING KITTEN TTS (KittenML/kitten-tts-nano-0.8) ===")
from kittentts import KittenTTS
t_load = time.time()
m = KittenTTS("KittenML/kitten-tts-nano-0.8")
load_time = time.time() - t_load

kitten_times = []
for i in range(3):
    t0 = time.time()
    audio = m.generate(test_phrase, voice="Jasper", speed=1.25)
    gen_time = time.time() - t0
    kitten_times.append(gen_time)

k_duration = len(audio) / 24000.0
k_avg_gen = sum(kitten_times) / len(kitten_times)
k_rtf = k_avg_gen / k_duration
k_speed_mult = k_duration / k_avg_gen
print(f"KittenTTS (Jasper): Duration: {k_duration:.2f}s | Gen Time: {k_avg_gen:.2f}s | RTF: {k_rtf:.2f} | Speed: {k_speed_mult:.2f}x real-time")
