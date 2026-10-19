import os
import urllib.request
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL_URL = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v1.0.onnx"
VOICES_URL = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices-v1.0.bin"
os.makedirs("video-output", exist_ok=True)

def download(url, path):
    if not os.path.exists(path):
        print(f"Downloading {os.path.basename(path)}...")
        urllib.request.urlretrieve(url, path)

download(MODEL_URL, "kokoro-v1.0.onnx")
download(VOICES_URL, "voices-v1.0.bin")

topic = os.getenv("VIDEO_TOPIC", "Long Handle Floor Scrub Brush with Squeegee").strip()
# Use factual, conservative copy; no unsupported performance claims.
if "scrub brush" in topic.lower():
    narration = "Make cleaning easier with this long-handle scrub brush. Scrub away dirt, then clear water with the built-in squeegee. Shop now at Atlas Goods Store."
else:
    narration = f"Take a closer look at {topic}. Find product details and current availability at Atlas Goods Store."

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
samples, sample_rate = kokoro.create(narration, voice="bf_emma", speed=0.96, lang="en-gb")
sf.write("video-output/voiceover.wav", samples, sample_rate)
print(f"Generated British English narration ({len(samples) / sample_rate:.1f}s) with Kokoro voice bf_emma.")
