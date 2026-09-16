import time
from kittentts import KittenTTS

test_phrase = "I am your coding agent. All unit tests have passed, and your application is ready to ship."

print("Loading KittenTTS...")
t0 = time.time()
m = KittenTTS("KittenML/kitten-tts-nano-0.8")
print(f"Loaded in {time.time() - t0:.2f}s")

# Warm up
m.generate("Hello.", voice="Jasper", speed=1.25)

# Benchmark 3 runs
times = []
for i in range(3):
    t0 = time.time()
    audio = m.generate(test_phrase, voice="Jasper", speed=1.25)
    gen_time = time.time() - t0
    times.append(gen_time)
    print(f"Run {i+1}: {gen_time:.3f}s")

dur = len(audio) / 24000.0
avg_time = sum(times) / len(times)
rtf = avg_time / dur
speed = dur / avg_time
print(f"KittenTTS (Jasper): Duration: {dur:.2f}s | Avg Gen: {avg_time:.3f}s | RTF: {rtf:.2f} | Speed: {speed:.1f}x real-time")
