"""Videonun başına Türkçe yapay zeka anlatıcı ekler (film sesi o sırada kısılır).
python anlatici.py video.mp4 "metin" cikti.mp4"""
import json, subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))

def ekle(video, metin, cikti, ses="tr-TR-AhmetNeural"):
    mp3 = tempfile.mktemp(suffix=".mp3")
    subprocess.run([sys.executable, os.path.join(here, "tts.py"), metin, mp3, ses], check=True)
    d = float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", mp3],
                                        capture_output=True, text=True).stdout)["format"]["duration"])
    fc = (f"[0:a]volume='if(lt(t,{d + 0.6:.2f}),0.22,1)':eval=frame[a0];"
          "[1:a]adelay=300|300,volume=1.5[n];[a0][n]amix=inputs=2:duration=first:normalize=0[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", mp3, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", cikti], check=True)
    os.remove(mp3)

if __name__ == "__main__":
    ekle(*sys.argv[1:4])
