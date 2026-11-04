"""Bir filmi sahne geçişlerine göre partlara bölüp dikey (9:16) Reels videolarına çevirir.

Kullanım:
    python parts.py film.mp4 --baslik "Nosferatu (1922)" --cikti ciktilar/ [--altyazi film.srt]

Her part: bulanık arka planlı 1080x1920 video, üstte film adı, altta "Part 3/12" yazısı,
varsa altyazı. Partlar sahne ortasında değil, sahne geçişlerinde kesilir.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sure(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def sahne_gecisleri(path, esik=0.3):
    """Sahne geçişlerinin saniye cinsinden listesi (ffmpeg ile, küçük çözünürlükte, hızlı)."""
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf",
         f"fps=6,scale=160:-2,select='gt(scene,{esik})',metadata=print:file=-", "-f", "null", "-"],
        capture_output=True, text=True, check=True).stdout
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", out)]


def partlara_bol(toplam, gecisler, en_az=60, en_fazla=180):
    """Her part en_az..en_fazla saniye olacak şekilde sahne geçişlerinden kesim noktası seçer."""
    noktalar, bas = [], 0.0
    while toplam - bas > en_fazla:
        adaylar = [g for g in gecisler if bas + en_az <= g <= bas + en_fazla]
        kesim = adaylar[-1] if adaylar else bas + en_fazla  # uygun geçiş yoksa zorla kes
        noktalar.append((bas, kesim))
        bas = kesim
    if toplam - bas < en_az / 2 and noktalar:  # çok kısa son parçayı öncekine ekle
        noktalar[-1] = (noktalar[-1][0], toplam)
    else:
        noktalar.append((bas, toplam))
    return noktalar


def yazi(metin):
    return metin.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def srt_kaydir(srt, bas, hedef):
    """Altyazı zamanlarını partın başına göre kaydırır (part 00:00'dan başlasın diye)."""
    def ms(t):
        h, m, r = t.split(":"); sn, mili = r.split(",")
        return ((int(h) * 60 + int(m)) * 60 + int(sn)) * 1000 + int(mili)
    def zaman(v):
        v = max(v, 0)
        return f"{v//3600000:02d}:{v//60000%60:02d}:{v//1000%60:02d},{v%1000:03d}"
    fark = int(bas * 1000)
    metin = Path(srt).read_text(encoding="utf-8", errors="replace")
    metin = re.sub(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)",
                   lambda m: f"{zaman(ms(m[1]) - fark)} --> {zaman(ms(m[2]) - fark)}", metin)
    Path(hedef).write_text(metin, encoding="utf-8")
    return str(hedef)


def part_render(girdi, cikti, bas, bit, baslik, no, toplam_part, altyazi=None):
    vf = (
        "[0:v]split[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.15[bg];"
        "[b]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"drawtext=fontfile={FONT}:text='{yazi(baslik)}':fontsize=64:fontcolor=white:"
        "borderw=4:bordercolor=black:x=(w-tw)/2:y=260,"
        f"drawtext=fontfile={FONT}:text='Part {no}/{toplam_part}':fontsize=80:fontcolor=yellow:"
        "borderw=5:bordercolor=black:x=(w-tw)/2:y=h-420"
    )
    if altyazi:
        altyazi = srt_kaydir(altyazi, bas, Path(cikti).with_suffix(".srt"))
        vf += (f",subtitles='{altyazi}':force_style='Fontname=DejaVu Sans,Fontsize=14,"
               "Outline=2,MarginV=110,Alignment=2'")
    vf += "[v]"
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{bas:.3f}", "-to", f"{bit:.3f}", "-i", str(girdi),
           "-sn", "-filter_complex", vf, "-map", "[v]", "-map", "0:a?",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(cikti)]
    subprocess.run(cmd, check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("girdi")
    p.add_argument("--baslik", required=True)
    p.add_argument("--cikti", default="ciktilar")
    p.add_argument("--altyazi")
    p.add_argument("--en-az", type=int, default=60)
    p.add_argument("--en-fazla", type=int, default=180)
    p.add_argument("--sadece", type=int, help="yalnızca bu partı üret (deneme için)")
    a = p.parse_args()

    out = Path(a.cikti)
    out.mkdir(parents=True, exist_ok=True)
    toplam = sure(a.girdi)
    noktalar = partlara_bol(toplam, sahne_gecisleri(a.girdi), a.en_az, a.en_fazla)
    plan = []
    for i, (bas, bit) in enumerate(noktalar, 1):
        dosya = out / f"part_{i:02d}.mp4"
        plan.append({"part": i, "toplam": len(noktalar), "bas": round(bas, 2), "bit": round(bit, 2),
                     "dosya": str(dosya), "paylasildi": False})
        if a.sadece and i != a.sadece:
            continue
        part_render(a.girdi, dosya, bas, bit, a.baslik, i, len(noktalar), a.altyazi)
        print(f"Part {i}/{len(noktalar)}: {bas:.0f}-{bit:.0f} sn -> {dosya}")
    (out / "plan.json").write_text(json.dumps({"baslik": a.baslik, "partlar": plan},
                                              ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
