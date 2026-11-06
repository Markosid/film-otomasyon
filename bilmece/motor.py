"""Ortak bilmece video motoru: koyu grenli tarz, başlık, yazı hapları, altyazı, olay kaydı tablosu, ses/müzik/efekt."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sfx

W, H, FPS = 1080, 1920, 30
SAH = 1240
FD = "/usr/share/fonts/truetype/"
SERIF = lambda s: ImageFont.truetype(FD + "freefont/FreeSerifItalic.ttf", s)
MONO = lambda s: ImageFont.truetype(FD + "jetbrains-mono/JetBrainsMono-Bold.ttf", s)
KALIN = lambda s: ImageFont.truetype(FD + "dejavu/DejaVuSans-Bold.ttf", s)
CIZ = (14, 14, 18)
KIRMIZI, SARI, YESIL, KREM = (226, 52, 52), (240, 196, 80), (80, 190, 120), (240, 236, 225)
lerp = lambda a, b, r: tuple(int(a[i] + (b[i] - a[i]) * r) for i in range(3))

_rng = np.random.default_rng(3)
GREN = [Image.fromarray(_rng.integers(0, 255, (H, W), dtype=np.uint8), "L").point(lambda v: 22 if v > 200 else 0) for _ in range(4)]
VIN = Image.new("L", (W, SAH), 0)
_vd = ImageDraw.Draw(VIN)
for _i in range(60):
    _vd.rectangle([_i * 6, _i * 6, W - _i * 6, SAH - _i * 6], outline=int(255 * (_i / 60) ** 0.6))
VIN = VIN.filter(ImageFilter.GaussianBlur(40))
SIYAH = Image.new("RGB", (W, H), (0, 0, 0))
KOYU = Image.new("RGB", (W, SAH), (8, 8, 12))


# ---------- karakter ----------
def kisi(d, x, y, s=1.0, govde=(200, 90, 60), ten=(232, 190, 150), sac=(60, 40, 28), adim=0.0, agiz="duz", el=("yan", "yan"),
         yon=1, kadin=False, gozler="acik", t=0.0, pantolon=(50, 56, 80), kep=None, gozluk=False, kravat=None, sakal=None, atki=None):
    k = lambda v: v * s
    zip_ = abs(math.sin(adim)) * k(8)
    d.ellipse([x - k(70), y - k(10), x + k(70), y + k(14)], fill=(0, 0, 0))
    gy = y - k(110) - zip_
    for f in (0, math.pi):
        a = math.sin(adim + f) * 0.45
        ux = x + math.sin(a) * k(70)
        d.line([(x, gy), (ux, y)], fill=pantolon, width=int(k(22)))
        d.ellipse([ux - k(16) + yon * k(6), y - k(9), ux + k(16) + yon * k(6), y + k(9)], fill=(30, 30, 30))
    if kadin:
        d.polygon([(x - k(60), gy + k(20)), (x + k(60), gy + k(20)), (x + k(38), gy - k(150)), (x - k(38), gy - k(150))], fill=govde, outline=CIZ)
    else:
        d.rounded_rectangle([x - k(42), gy - k(150), x + k(42), gy + k(6)], int(k(20)), fill=govde, outline=CIZ, width=int(k(4)))
    if kravat:
        d.polygon([(x - k(10), gy - k(148)), (x + k(10), gy - k(148)), (x + k(14), gy - k(60)), (x, gy - k(42)), (x - k(14), gy - k(60))], fill=kravat, outline=CIZ)
        d.polygon([(x - k(30), gy - k(150)), (x, gy - k(118)), (x + k(30), gy - k(150))], fill=(240, 240, 240), outline=CIZ)
    for i, taraf in enumerate((-1, 1)):
        ox, oy = x + taraf * k(38), gy - k(135)
        e = el[i]
        if e == "yukari":
            ex, ey = ox + taraf * k(55), oy - k(80)
        elif e == "ileri":
            ex, ey = ox + yon * k(85), oy + k(10)
        elif e == "bel":
            ex, ey = ox + taraf * k(40), oy + k(60)
        elif e == "bas":  # kafa kaşıma
            ex, ey = x + taraf * k(30), gy - k(250)
        else:
            ex, ey = ox + taraf * k(12) + math.sin(adim + i * math.pi) * k(25), oy + k(105)
        d.line([(ox, oy), (ex, ey)], fill=govde, width=int(k(20)))
        d.ellipse([ex - k(13), ey - k(13), ex + k(13), ey + k(13)], fill=ten, outline=CIZ, width=int(k(3)))
    hx, hy, r = x, gy - k(205), k(55)
    if kadin:
        d.ellipse([hx - r - k(12), hy - r - k(6), hx + r + k(12), hy + r * 0.9], fill=sac)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=ten, outline=CIZ, width=int(k(4)))
    d.chord([hx - r, hy - r - k(4), hx + r, hy + k(4)], 180, 360, fill=sac)
    if kadin:
        d.ellipse([hx - k(20), hy - r - k(40), hx + k(20), hy - r + k(2)], fill=sac)  # topuz
    if kep:
        d.chord([hx - r, hy - r - k(10), hx + r, hy + k(5)], 180, 360, fill=kep)
        d.rectangle([hx + yon * k(10) - k(10), hy - k(12), hx + yon * k(80), hy - k(2)], fill=kep)
    if sakal:
        d.chord([hx - r + k(4), hy - k(10), hx + r - k(4), hy + r + k(6)], 0, 180, fill=sakal)
    if atki:
        d.rounded_rectangle([hx - k(46), hy + r - k(14), hx + k(46), hy + r + k(16)], int(k(12)), fill=atki, outline=CIZ, width=int(k(3)))
    gx = hx + yon * k(14)
    kirp = (t + x * 0.0013) % 3.3 < 0.13
    for e in (-1, 1):
        ex_ = gx + e * k(18)
        if gozler == "kapali" or kirp:
            d.arc([ex_ - k(10), hy - k(8), ex_ + k(10), hy + k(6)], 20, 160, fill=CIZ, width=int(k(4)))
        elif gozler == "buyuk":
            d.ellipse([ex_ - k(13), hy - k(14), ex_ + k(13), hy + k(12)], fill=(255, 255, 255), outline=CIZ, width=int(k(3)))
            d.ellipse([ex_ - k(5), hy - k(5), ex_ + k(5), hy + k(5)], fill=CIZ)
        elif gozler == "yorgun":
            d.ellipse([ex_ - k(7), hy - k(5), ex_ + k(7), hy + k(8)], fill=CIZ)
            d.line([(ex_ - k(11), hy - k(4)), (ex_ + k(11), hy - k(4))], fill=ten, width=int(k(6)))
            d.arc([ex_ - k(10), hy + k(4), ex_ + k(10), hy + k(16)], 20, 160, fill=(150, 110, 120), width=int(k(3)))
        else:
            d.ellipse([ex_ - k(7), hy - k(8), ex_ + k(7), hy + k(8)], fill=CIZ)
            d.ellipse([ex_ - k(2), hy - k(6), ex_ + k(2), hy - k(2)], fill=(255, 255, 255))
        if gozluk:
            d.ellipse([ex_ - k(16), hy - k(14), ex_ + k(16), hy + k(14)], outline=CIZ, width=int(k(4)))
    d.ellipse([gx - k(42), hy + k(6), gx - k(28), hy + k(18)], fill=lerp(ten, (230, 120, 120), 0.5))
    d.ellipse([gx + k(28), hy + k(6), gx + k(42), hy + k(18)], fill=lerp(ten, (230, 120, 120), 0.5))
    if agiz == "gulen":
        d.chord([gx - k(20), hy + k(10), gx + k(20), hy + k(42)], 0, 180, fill=(110, 30, 30), outline=CIZ)
    elif agiz == "o":
        d.ellipse([gx - k(12), hy + k(18), gx + k(12), hy + k(44)], fill=(110, 30, 30), outline=CIZ)
    elif agiz == "uzgun":
        d.arc([gx - k(16), hy + k(26), gx + k(16), hy + k(46)], 200, 340, fill=CIZ, width=int(k(5)))
    elif agiz == "sirit":
        d.arc([gx - k(20), hy + k(12), gx + k(24), hy + k(36)], 10, 150, fill=CIZ, width=int(k(5)))
    else:
        d.line([(gx - k(12), hy + k(30)), (gx + k(12), hy + k(30))], fill=CIZ, width=int(k(5)))
    return hx, hy - r


# ---------- yazı öğeleri ----------
def hap(d, x, y, kel, kutu, yazi, boy=58):
    f = KALIN(boy)
    for k, kb, yb in zip(kel, kutu, yazi):
        w = d.textlength(k, font=f)
        d.rounded_rectangle([x, y, x + w + 36, y + boy + 30], 10, fill=kb, outline=CIZ, width=4)
        d.text((x + 18, y + 12), k, font=f, fill=yb)
        x += w + 50
    return x


def hap2(d, x, y, a, b, renk=KIRMIZI, boy=58):
    """[krem a][renkli b] kısa yolu"""
    return hap(d, x, y, [a, b], [KREM, renk], [CIZ, CIZ if renk in (SARI, YESIL) else (255, 255, 255)], boy)


def soru_isareti(d, x, y, s, rr):
    f = KALIN(int(s))
    d.text((x + 8, y + 8), "?", font=f, fill=(60, 10, 10), anchor="mm")
    d.text((x, y), "?", font=f, fill=lerp(KIRMIZI, (255, 120, 120), rr), anchor="mm")


def geri_sayim(d, kalan, x=540, y=560):
    if kalan >= 5.2:
        return
    n = max(1, math.ceil(kalan - 0.2))
    d.ellipse([x - 140, y - 140, x + 140, y + 140], fill=(0, 0, 0), outline=KIRMIZI, width=10)
    d.arc([x - 140, y - 140, x + 140, y + 140], -90, -90 + 360 * (1 - (kalan - 0.2) / 5), fill=(255, 255, 255), width=10)
    d.text((x, y), str(min(5, n)), font=KALIN(170), fill=(255, 255, 255), anchor="mm")


def zzz(d, x, y, t):
    for j in range(3):
        f = (t * 0.8 + j / 3) % 1
        d.text((x + f * 90 + j * 10, y - f * 160), "z", font=KALIN(int(40 + f * 40)), fill=lerp((240, 240, 255), (70, 80, 110), f))


def altyazi(d, metin, t, sure):
    kel = metin.split()
    n = max(1, len(kel))
    k = min(n - 1, int(t / max(0.01, sure - 0.6) * n))
    bas = (k // 4) * 4
    s = " ".join(kel[bas:bas + 4])
    boy = 54
    while d.textlength(s, font=KALIN(boy)) > 960:
        boy -= 2
    f = KALIN(boy)
    w = d.textlength(s, font=f)
    y = SAH - 150
    d.rounded_rectangle([W / 2 - w / 2 - 26, y - 8, W / 2 + w / 2 + 26, y + 70], 14, fill=(0, 0, 0))
    d.text((W / 2, y + 31), s, font=f, fill=(255, 255, 255), anchor="mm")


def ust_baslik(d, baslik, etiket, no, gece=True):
    d.text((62, 72), baslik, font=SERIF(104), fill=(20, 20, 24))
    d.text((58, 68), baslik, font=SERIF(104), fill=(245, 240, 228))
    d.text((62, 200), etiket, font=MONO(30), fill=(220, 215, 200))
    d.rounded_rectangle([W - 300, 80, W - 60, 140], 30, fill=(20, 20, 24), outline=(120, 120, 120), width=2)
    d.ellipse([W - 282, 100, W - 262, 120], fill=KIRMIZI if gece else SARI)
    d.text((W - 170, 110), f"BİLMECE #{no}", font=MONO(28), fill=(230, 230, 230), anchor="mm")


def alt_panel(d, buyuk, t, kayit, satirlar, no):
    """satirlar: [(ad, deger, renk)]; deger None ise boş."""
    d.rectangle([0, SAH, W, H], fill=(16, 16, 20))
    d.line([(0, SAH), (W, SAH)], fill=(60, 60, 70), width=3)
    boy = 104
    while d.textlength(buyuk, font=KALIN(boy)) > 980:
        boy -= 4
    d.text((W // 2, SAH + 120), buyuk, font=KALIN(boy), fill=lerp((16, 16, 20), (242, 238, 225), min(1, t / 0.35)), anchor="mm")
    d.text((60, SAH + 230), kayit, font=MONO(30), fill=(130, 130, 140))
    d.line([(60, SAH + 278), (W - 60, SAH + 278)], fill=(60, 60, 70), width=2)
    for j, (ad, deger, renk) in enumerate(satirlar):
        y = SAH + 300 + j * 82
        d.text((60, y), ad, font=MONO(40), fill=(160, 160, 170))
        if deger:
            d.text((W - 60, y), deger, font=MONO(42), fill=renk, anchor="ra")
        d.line([(60, y + 64), (W - 60, y + 64)], fill=(40, 40, 48), width=1)
    d.text((60, H - 70), f"bilmece #{no} · temsilî çizim", font=MONO(26), fill=(90, 90, 100))
    d.text((W - 60, H - 70), "@bilmece.sokagi", font=MONO(26), fill=(90, 90, 100), anchor="ra")


def son_islem(im, toplam_t, t, aydinlik=0.0, sars=0):
    sahne = im.crop((0, 0, W, SAH))
    sahne = Image.composite(KOYU, sahne, VIN.point(lambda v: int(v * (0.75 - 0.35 * aydinlik))))
    im.paste(sahne, (0, 0))
    return im


def bitir(im, toplam_t, t, sars=0):
    im = Image.composite(SIYAH, im, GREN[int(toplam_t * FPS) % 4])
    if sars:
        im = im.transform(im.size, Image.AFFINE, (1, 0, sars, 0, 1, 0), fillcolor=(16, 16, 20))
    if t < 0.2:
        im = Image.blend(Image.new("RGB", im.size, (10, 10, 14)), im, t / 0.2)
    return im


# ---------- üretim hattı ----------
def sure_al(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def uret(ad, SAHNE, cerceve, olay_fn, cikti, ses="tr-TR-AhmetNeural", ekler=None, minor=False, muzik_ses=0.22, motor_bitis=None):
    klasor = f"ses_{ad}_{ses}"
    os.makedirs(klasor, exist_ok=True)
    sureler = []
    for i, sc in enumerate(SAHNE):
        f = f"{klasor}/{i}.mp3"
        if not os.path.exists(f):
            subprocess.run(["python3", "ses.py", sc[1], f, ses, "-6Hz" if ses.startswith("tr") else "-0Hz", "-4%"], check=True)
        sureler.append(sure_al(f) + (ekler or {}).get(sc[0], 0.6))
    bas = [sum(sureler[:i]) for i in range(len(sureler))]
    liste = []
    for i, s in enumerate(sureler):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{klasor}/{i}.mp3", "-af", f"apad=whole_dur={s}", "-ar", "44100", "-ac", "2", f"{klasor}/p{i}.wav"], check=True)
        liste.append(f"file 'p{i}.wav'")
    open(f"{klasor}/liste.txt", "w").write("\n".join(liste))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{klasor}/liste.txt",
                    "-af", "equalizer=f=140:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3", f"{klasor}/anlatim.wav"], check=True)
    sfx.karistir(f"{klasor}/efekt.wav", sum(sureler), olay_fn(bas, sureler), muzik_ses=muzik_ses, minor=minor, motor_bitis=motor_bitis)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{klasor}/anlatim.wav", "-i", f"{klasor}/efekt.wav", "-filter_complex",
                    "[0][1]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95", f"{klasor}/tum.wav"], check=True)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", f"{klasor}/tum.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-tune", "grain", "-maxrate", "6M",
                            "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", cikti], stdin=subprocess.PIPE)
    for i, s in enumerate(sureler):
        for n in range(int(s * FPS)):
            enc.stdin.write(cerceve(i, n / FPS, s, bas[i] + n / FPS, bas, sureler).tobytes())
    enc.stdin.close(); enc.wait()
    print(cikti, round(sum(sureler), 1), "sn")
