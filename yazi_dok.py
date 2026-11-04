"""Videodaki konuşmaları yazıya döker (İngilizce) -> SRT. python yazi_dok.py video.mp4 cikti.srt"""
import subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(audio, language="en", vad_filter=True)
def z(t): return f"{int(t//3600):02d}:{int(t//60%60):02d}:{int(t%60):02d},{int(t*1000%1000):03d}"
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{z(s.start)} --> {z(s.end)}\n{s.text.strip()}\n\n")
