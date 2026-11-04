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


HESAP = "@eskisinema.arsivi"
MOR = "0xB57BFF"
SORULAR_DEVAM = ["Sence sonra ne olacak?", "Sen olsan ne yapardın?", "Bu sahnede kimin tarafındasın?"]
SORULAR_SON = ["İzlediyseniz tek kelimeyle anlatın", "Bu filme 10 üzerinden kaç verirsin?", "Buna benzer bir film önerin"]


def satirlar(metin, en_fazla=24):
    """Metni kelime bölmeden en fazla 2-3 satıra ayırır."""
    out, cur = [], ""
    for k in metin.split():
        if cur and len(cur) + 1 + len(k) > en_fazla:
            out.append(cur); cur = k
        else:
            cur = f"{cur} {k}".strip()
    return out + ([cur] if cur else [])


def render(girdi, cikti, bas, bit, baslik, kanca, kredi, son_yazi="", fade=True, altyazi=None, soru=None):
    """Siyah zemin; üstte mor çizgili kanca, ortada film, altta etkileşim sorusu + takip çağrısı."""
    if soru is None:
        liste = SORULAR_SON if fade else SORULAR_DEVAM
        soru = liste[sum(map(ord, baslik)) % len(liste)]
    VY = 560  # videonun üst kenarı
    sat = satirlar(kanca, 22) if kanca else []
    fs = min(68, boyut(max(sat, key=len) if sat else "", 68, 900))
    ust = VY - 70 - len(sat) * int(fs * 1.25)
    vf = ("[0:v]crop='min(iw,ih*1.45)':ih,scale=1080:-2,pad=1080:1920:0:" + str(VY) + ":black,"
          f"drawtext=fontfile={FONT}:text='{yazi(baslik)}':fontsize={boyut(baslik, 40)}:fontcolor={MOR}:x=100:y={ust - 70}")
    if sat:
        vf += f",drawbox=x=66:y={ust - 6}:w=10:h={len(sat) * int(fs * 1.25) - 4}:color={MOR}:t=fill"
        for n, m in enumerate(sat):
            vf += f",drawtext=fontfile={FONT}:text='{yazi(m)}':fontsize={fs}:fontcolor=white:x=100:y={ust + n * int(fs * 1.25)}"
    vf += (f",drawtext=fontfile={FONT}:text='{yazi(HESAP)}':fontsize=30:fontcolor=white@0.45:x=24:y={VY + 24}"
           f",drawtext=fontfile={FONT}:text='{yazi(soru)} ↓':fontsize={boyut(soru + ' ↓', 50, 920)}:fontcolor=white:x=80:y=1430"
           f",drawtext=fontfile={FONT}:text='Her gün yeni part için':fontsize=40:fontcolor={MOR}:x=80:y=1520"
           f",drawtext=fontfile={FONT}:text='takip et → {yazi(HESAP)}':fontsize=40:fontcolor={MOR}:x=80:y=1572"
           f",drawtext=fontfile={FONT}:text='{yazi(kredi)}':fontsize=26:fontcolor=white@0.6:x=(w-tw)/2:y=h-150")
    if son_yazi:  # son 3 saniyede büyük "devamı" yazısı
        vf += (f",drawtext=fontfile={FONT}:text='{yazi(son_yazi)}':fontsize={boyut(son_yazi, 88, 960)}:fontcolor=white:box=1:boxcolor=red@0.85:"
               f"boxborderw=24:x=(w-tw)/2:y=(h-th)/2+520:enable='gte(t,{bit-bas-3:.2f})'")
    if altyazi:  # SRT film zamanına göre; part başına kaydırılır
        from parts import srt_kaydir
        kayik = srt_kaydir(altyazi, bas, str(cikti) + ".srt")
        vf += (f",subtitles='{kayik}':force_style='Fontname=DejaVu Sans,Bold=1,Fontsize=9,"
               "Outline=2,Shadow=0,MarginV=104,Alignment=2'")
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
