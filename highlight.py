"""Bir animasyon filminin en hareketli/sesli bölümünü bulup dikey (9:16) Reels'e çevirir.

Kullanım:
    python highlight.py film.mp4 --baslik "Sintel (2010)" --kanca "Ejderhasını kaybettiği an..." \
        --kredi "Sintel · Blender Foundation · CC BY 3.0" --cikti out/sintel_01.mp4 [--bas 297.3 --bit 339.3]

Seçim: sahne geçişlerinde başlayıp biten 40-60 sn'lik pencerelerden ses yüksekliği + kesme sıklığı
en yüksek olan seçilir (jenerik hariç).
"""
import argparse, re, subprocess

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def yazi(m):
    return m.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%").replace(",", "\\,")


def analiz(path):
    s = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-an", "-vf",
                        "fps=6,scale=160:-2,select='gt(scene,0.25)',metadata=print:file=-", "-f", "null", "-"],
                       capture_output=True, text=True, check=True).stdout
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-af",
                        "asetnsamples=48000,astats=metadata=1:reset=1,"
                        "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"],
                       capture_output=True, text=True, check=True).stdout
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", s)]
    rms = [float(x) if x != "-inf" else -90.0 for x in re.findall(r"RMS_level=(\S+)", a)]
    return cuts, rms


def en_iyi(cuts, rms, son, en_az=40, en_fazla=60):
    best = None
    for s in cuts:
        for e in cuts:
            L = e - s
            if en_az <= L <= en_fazla and s > 20 and e < son:
                puan = sum(rms[int(s):int(e)]) / L + 40 * sum(1 for x in cuts if s < x < e) / L
                if best is None or puan > best[0]:
                    best = (puan, s, e)
    return best[1], best[2]


def boyut(metin, en_fazla, genislik=1000):
    """Yazı ekrana sığsın diye punto (DejaVu Bold ~0.63 em/karakter)."""
    return int(min(en_fazla, genislik / (0.63 * max(len(metin), 1))))


def render(girdi, cikti, bas, bit, baslik, kanca, kredi, son_yazi="", fade=True, altyazi=None):
    vf = ("[0:v]split[a][b];"
          "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.2[bg];"
          "[b]crop='min(iw,ih*1.45)':ih,scale=1080:-2[fg];"
          "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
          f"drawtext=fontfile={FONT}:text='{yazi(baslik)}':fontsize={boyut(baslik, 70)}:fontcolor=white:borderw=4:bordercolor=black:x=(w-tw)/2:y=300,"
          f"drawtext=fontfile={FONT}:text='{yazi(kanca)}':fontsize={boyut(kanca, 56)}:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-tw)/2:y=h-480"
          + (f":enable='lt(t,{bit-bas-3:.2f})'" if son_yazi else "") + ","
          f"drawtext=fontfile={FONT}:text='{yazi(kredi)}':fontsize=30:fontcolor=white@0.8:borderw=2:bordercolor=black:x=(w-tw)/2:y=h-200")
    if son_yazi:  # son 3 saniyede büyük "devamı" yazısı
        vf += (f",drawtext=fontfile={FONT}:text='{yazi(son_yazi)}':fontsize={boyut(son_yazi, 88, 960)}:fontcolor=white:box=1:boxcolor=red@0.85:"
               f"boxborderw=24:x=(w-tw)/2:y=(h-th)/2+520:enable='gte(t,{bit-bas-3:.2f})'")
    if altyazi:  # SRT film zamanına göre; part başına kaydırılır
        from parts import srt_kaydir
        kayik = srt_kaydir(altyazi, bas, str(cikti) + ".srt")
        vf += (f",subtitles='{kayik}':force_style='Fontname=DejaVu Sans,Bold=1,Fontsize=9,"
               "Outline=2,Shadow=0,MarginV=95,Alignment=2'")
    vf += "[v]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{bas:.3f}", "-to", f"{bit:.3f}", "-i", girdi,
                    "-filter_complex", vf, "-map", "[v]", "-map", "0:a?",
                    *(["-af", f"afade=t=out:st={bit-bas-1.5:.2f}:d=1.5"] if fade else []),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", cikti], check=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("girdi"); p.add_argument("--cikti", required=True)
    p.add_argument("--baslik", required=True); p.add_argument("--kanca", default="")
    p.add_argument("--kredi", required=True)
    p.add_argument("--bas", type=float); p.add_argument("--bit", type=float)
    p.add_argument("--son-yazi", default="", help="son 3 sn'de gösterilecek yazı, örn. DEVAMI PART 2'DE")
    p.add_argument("--kesik", action="store_true", help="sesi kısmadan aniden kes (merak bırakır)")
    p.add_argument("--jenerik", type=float, default=0, help="jeneriğin başladığı saniye")
    a = p.parse_args()
    if a.bas is None:
        cuts, rms = analiz(a.girdi)
        a.bas, a.bit = en_iyi(cuts, rms, a.jenerik or len(rms))
    print(f"Seçilen bölüm: {a.bas:.1f}-{a.bit:.1f} sn")
    render(a.girdi, a.cikti, a.bas, a.bit, a.baslik, a.kanca, a.kredi, a.son_yazi, not a.kesik)
