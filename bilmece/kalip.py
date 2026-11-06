"""Hazır bilmece kalıbı: bilmeceler.py'deki veriden video üretir.
Kullanım: python3 kalip.py 1 [2 3 ...]   (çıktı: stok/bilmece01.mp4)"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont
from motor import *
from bilmeceler import BILMECELER

EMOJI_F = ImageFont.truetype(FD + "noto/NotoColorEmoji.ttf", 109)
_emo = {}


def emoji(ch, boy):
    if (ch, boy) not in _emo:
        im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((110, 110), ch, font=EMOJI_F, embedded_color=True, anchor="mm")
        im = im.crop(im.getbbox())
        r = boy / max(im.size)
        _emo[(ch, boy)] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _emo[(ch, boy)]


def koy(im, ch, x, y, boy):
    e = emoji(ch, max(8, int(boy)))
    im.paste(e, (int(x - e.width / 2), int(y - e.height / 2)), e)


ZEMIN_Y = 1060
TIP = {  # karakter kalıpları
    "adam": dict(govde=(60, 90, 150), sac=(50, 34, 24)),
    "kadin": dict(govde=(170, 60, 90), sac=(90, 50, 30), kadin=True),
    "cocuk": dict(govde=(230, 150, 40), sac=(70, 45, 25), s=0.62),
    "kiz": dict(govde=(200, 90, 160), sac=(110, 60, 30), kadin=True, s=0.62),
    "yasli": dict(govde=(110, 90, 70), sac=(205, 205, 205), gozluk=True, sakal=(215, 215, 215)),
    "nine": dict(govde=(120, 80, 110), sac=(210, 210, 210), gozluk=True, kadin=True),
    "doktor": dict(govde=(235, 235, 240), sac=(40, 30, 20), gozluk=True, pantolon=(80, 110, 150)),
    "doktor_k": dict(govde=(235, 235, 240), sac=(60, 36, 24), kadin=True),
    "ciftci": dict(govde=(150, 100, 50), kep=(180, 40, 40), pantolon=(50, 70, 120), sakal=(90, 70, 50)),
    "sofor": dict(govde=(70, 110, 80), kep=(30, 40, 60)),
    "ogretmen": dict(govde=(120, 60, 120), sac=(60, 40, 30), gozluk=True, kadin=True),
    "kel": dict(govde=(90, 110, 140), sac=(232, 190, 150), sakal=(80, 60, 45)),
    "kisa": dict(govde=(90, 140, 90), sac=(40, 30, 20), s=0.6, kravat=(200, 60, 60)),
    "usta": dict(govde=(230, 140, 40), kep=(240, 200, 60), pantolon=(60, 60, 80)),
}
XLER = {1: [330], 2: [250, 560], 3: [200, 440, 680]}


# ---------- mekânlar ----------
def m_oda(d, karanlik=False):
    duvar = (52, 46, 60) if karanlik else (88, 72, 70)
    d.rectangle([0, 0, W, SAH], fill=duvar)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, ZEMIN_Y - 120)], fill=lerp(duvar, (255, 255, 255), 0.04), width=8)
    d.rectangle([0, ZEMIN_Y - 120, W, SAH], fill=lerp(duvar, (40, 30, 20), 0.5))
    d.rectangle([700, 300, 960, 560], fill=(30, 36, 60) if karanlik else (170, 200, 220), outline=CIZ, width=8)
    d.line([(830, 300), (830, 560)], fill=CIZ, width=6); d.line([(700, 430), (960, 430)], fill=CIZ, width=6)
    if karanlik:
        d.ellipse([870, 330, 930, 390], fill=(235, 230, 200))
    d.ellipse([140, ZEMIN_Y - 40, 940, ZEMIN_Y + 60], fill=(110, 56, 56), outline=CIZ, width=4)


def m_mutfak(d):
    d.rectangle([0, 0, W, SAH], fill=(196, 206, 200))
    for x in range(0, W, 70):
        for y in range(300, ZEMIN_Y - 230, 70):
            d.rectangle([x, y, x + 68, y + 68], outline=(176, 188, 182), width=2)
    d.rectangle([0, ZEMIN_Y - 230, W, ZEMIN_Y - 200], fill=(140, 110, 80), outline=CIZ, width=4)
    d.rectangle([0, ZEMIN_Y - 200, W, ZEMIN_Y - 100], fill=(170, 130, 90), outline=CIZ, width=4)
    d.rounded_rectangle([880, 420, 1040, ZEMIN_Y - 100], 14, fill=(235, 240, 245), outline=CIZ, width=6)  # buzdolabı
    d.line([(880, 600), (1040, 600)], fill=CIZ, width=5); d.rectangle([895, 480, 905, 560], fill=(150, 150, 160))
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(150, 120, 100))


def m_kir(d):
    d.rectangle([0, 0, W, SAH], fill=(120, 170, 210))
    d.ellipse([820, 290, 960, 430], fill=(250, 220, 120))
    d.ellipse([-200, 760, 700, 1100], fill=(90, 150, 80)); d.ellipse([400, 800, 1300, 1150], fill=(100, 160, 85))
    d.rectangle([700, 640, 1000, 900], fill=(170, 60, 50), outline=CIZ, width=6)
    d.polygon([(680, 650), (850, 530), (1020, 650)], fill=(120, 40, 36), outline=CIZ)
    d.rectangle([800, 760, 900, 900], fill=(90, 40, 30), outline=CIZ, width=4)
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(110, 150, 70))
    for x in range(0, W, 90):
        d.line([(x, ZEMIN_Y - 60), (x, ZEMIN_Y - 130)], fill=(150, 110, 70), width=10)
    d.line([(0, ZEMIN_Y - 115), (W, ZEMIN_Y - 115)], fill=(150, 110, 70), width=8)


def m_sokak(d, karanlik=False):
    gok = (30, 34, 60) if karanlik else (150, 180, 210)
    d.rectangle([0, 0, W, SAH], fill=gok)
    for i, (x, w, h, c) in enumerate(((0, 260, 640, (120, 90, 80)), (280, 220, 520, (90, 100, 120)), (520, 300, 760, (140, 120, 90)), (840, 240, 580, (100, 80, 90)))):
        top = ZEMIN_Y - 100 - h
        d.rectangle([x, top, x + w, ZEMIN_Y - 100], fill=c, outline=CIZ, width=5)
        for yy in range(top + 30, ZEMIN_Y - 160, 90):
            for xx in range(x + 25, x + w - 40, 70):
                d.rectangle([xx, yy, xx + 40, yy + 50], fill=(240, 220, 130) if karanlik and (xx + yy) % 3 else (60, 70, 90))
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(70, 70, 76))
    d.rectangle([0, ZEMIN_Y - 100, W, ZEMIN_Y - 80], fill=(150, 150, 150))


def m_yol(d):
    d.rectangle([0, 0, W, SAH], fill=(140, 180, 215))
    d.polygon([(0, 820), (300, 640), (620, 780), (900, 600), (W, 700), (W, 960), (0, 960)], fill=(110, 140, 110))
    d.rectangle([0, 940, W, SAH], fill=(60, 60, 66))
    for x in range(0, W, 160):
        d.rectangle([x, 1100, x + 90, 1115], fill=(240, 220, 120))
    d.rectangle([0, 930, W, 945], fill=(200, 200, 200))


def m_sinif(d):
    d.rectangle([0, 0, W, SAH], fill=(196, 180, 140))
    d.rectangle([100, 300, 980, 700], fill=(40, 70, 55), outline=(120, 80, 40), width=16)
    d.text((150, 340), "2 + 2 = ?", font=SERIF(60), fill=(230, 230, 220))
    d.line([(600, 380), (900, 380)], fill=(230, 230, 220), width=4)
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(140, 100, 70))


def m_hastane(d):
    d.rectangle([0, 0, W, SAH], fill=(200, 222, 228))
    d.rectangle([0, 760, W, 790], fill=(120, 170, 190))
    d.rounded_rectangle([760, 300, 960, 500], 16, fill=(255, 255, 255), outline=CIZ, width=6)
    d.rectangle([840, 330, 880, 470], fill=KIRMIZI); d.rectangle([790, 380, 930, 420], fill=KIRMIZI)
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(170, 190, 196))


def m_market(d):
    d.rectangle([0, 0, W, SAH], fill=(230, 220, 190))
    renk = [(220, 80, 70), (80, 160, 90), (240, 190, 70), (80, 130, 200)]
    for r in range(4):
        y = 330 + r * 150
        d.rectangle([60, y + 100, 1020, y + 116], fill=(120, 90, 60))
        for i in range(14):
            d.rounded_rectangle([70 + i * 68, y + 30, 120 + i * 68, y + 100], 6, fill=renk[(i + r) % 4], outline=CIZ, width=2)
    d.rectangle([0, ZEMIN_Y - 100, W, SAH], fill=(200, 200, 205))


def m_nehir(d):
    d.rectangle([0, 0, W, SAH], fill=(140, 190, 220))
    d.rectangle([0, 620, W, 940], fill=(60, 120, 170))
    for i in range(12):
        x = (i * 173) % W
        d.arc([x, 680 + (i % 4) * 60, x + 120, 720 + (i % 4) * 60], 200, 340, fill=(200, 230, 250), width=5)
    d.rectangle([0, 940, W, SAH], fill=(150, 130, 80))
    for x in (60, 980):
        d.ellipse([x - 70, 440, x + 70, 600], fill=(60, 130, 60)); d.rectangle([x - 12, 560, x + 12, 640], fill=(100, 70, 40))


MEKAN = {"oda": m_oda, "karanlik": lambda d: m_oda(d, True), "mutfak": m_mutfak, "kir": m_kir, "sokak": m_sokak,
         "gece": lambda d: m_sokak(d, True), "yol": m_yol, "sinif": m_sinif, "hastane": m_hastane, "market": m_market, "nehir": m_nehir}


def etiket(d, x, y, yazi, renk=KREM, yazi_renk=CIZ, olcek=1.0):
    f = KALIN(int(40 * olcek))
    w = d.textlength(yazi, font=f)
    d.rounded_rectangle([x - w / 2 - 18, y - 32 * olcek, x + w / 2 + 18, y + 32 * olcek], 10, fill=renk, outline=CIZ, width=4)
    d.text((x, y), yazi, font=f, fill=yazi_renk, anchor="mm")


UST = Image.new("L", (W, 300), 0)
for _y in range(300):
    ImageDraw.Draw(UST).line([(0, _y), (W, _y)], fill=int(190 * (1 - _y / 300) ** 1.3))
UST_SIYAH = Image.new("RGB", (W, 300), (10, 10, 14))


def fligran(im):
    """Sahnenin üstünde ince, yarı saydam @bilmece.sokagi yazısı."""
    kat = Image.new("RGBA", (W, SAH), (0, 0, 0, 0))
    kd = ImageDraw.Draw(kat)
    kd.text((W - 40, 262), "@bilmece.sokagi", font=MONO(30), fill=(255, 255, 255, 70), anchor="ra")
    kd.text((W / 2, SAH - 205), "@bilmece.sokagi", font=MONO(26), fill=(255, 255, 255, 55), anchor="mm")
    im.paste(kat, (0, 0), kat)


def hazirla(no):
    b = BILMECELER[no - 1]
    hik = b["s"]
    SAHNE = [(f"s{j}", s[0], s[1]) for j, s in enumerate(hik)]
    SAHNE += [("soru", b["soru"][0] + " Beş saniyen var. Cevabını yoruma yaz.", b["soru"][1]),
              ("cevap", b["cevap"][0], b["cevap"][1]), ("son", b["son"][0], b["son"][1])]
    n = len(hik)
    kisiler = b["kisiler"]
    xs = XLER[len(kisiler)]
    etk = "  ·  ".join(" ".join(r[0]) for r in b["panel"][:2]) + "  ·  ?"
    while d_olc.textlength(etk, font=MONO(30)) > 950:
        etk = etk.rsplit("  ·  ", 2)[0] + "  ·  ?"

    def satirlar(i, t):
        out = []
        for j, (ad, deger) in enumerate(b["panel"]):
            if j < len(b["panel"]) - 1:
                out.append((ad, deger if i >= j else None, KREM))
            elif i > n:
                out.append((ad, deger, SARI))
            else:
                out.append((ad, "?" if i == n else None, KIRMIZI if int(t * 3) % 2 else (120, 120, 130)))
        return out

    def cerceve(i, t, sure, T, bas, sureler):
        k, metin, buyuk = SAHNE[i]
        p = t / sure
        im = Image.new("RGB", (W, H), (16, 16, 20))
        d = ImageDraw.Draw(im)
        MEKAN[b["mekan"]](d)
        im.paste(UST_SIYAH, (0, 0), UST)
        cevap, son, soru = i == n + 1, i == n + 2, i == n
        for j, (tip, ad) in enumerate(kisiler):
            ozel = dict(TIP[tip]); s = ozel.pop("s", 0.85)
            ana = j == 0
            zip_ = abs(math.sin(T * 6 + j)) * 20 if (cevap and ana and p > 0.1) else 0
            if cevap or son:
                agiz, el, gz = "gulen", (("yukari", "yukari") if ana else ("yan", "yukari")), "buyuk" if ana and cevap else "acik"
            elif soru:
                agiz, el, gz = "o", (("bas", "yan") if j % 2 == 0 else ("yan", "bas")), "acik"
            else:
                konusan = (i % len(kisiler)) == j
                agiz = ("o" if int(T * 5) % 2 else "sirit") if konusan else "sirit"
                el, gz = (("ileri", "yan") if konusan else ("yan", "yan")), "acik"
            kisi(d, xs[j], ZEMIN_Y - zip_, s, t=T + j, gozler=gz, agiz=agiz, el=el, yon=1 if j < len(kisiler) - 1 or len(kisiler) == 1 else -1, **ozel)
            etiket(d, xs[j], ZEMIN_Y - 370 * s - 70 - zip_, ad, SARI if cevap and ana else KREM, CIZ, 0.8 if len(ad) > 9 else 0.9)
        # nesneler
        if i < n:
            em = hik[i][2]
            for q, ch in enumerate(em):
                a = min(1, max(0, (t - 0.25 - q * 0.5) / 0.3))
                if a > 0:
                    boy = 230 * (a if a < 1 else 1) * (1 + 0.15 * math.sin(min(1, a) * math.pi))
                    koy(im, ch, 860 - q * 220, 560 + 14 * math.sin(T * 2 + q), boy)
            if p > 0.12:
                kel = hik[i][3]
                hap(d, 70, 290, kel, [KREM] * (len(kel) - 1) + [KIRMIZI], [CIZ] * (len(kel) - 1) + [(255, 255, 255)], 56)
        if soru:
            soru_isareti(d, 900, 800, 260 + 20 * math.sin(t * 4), abs(math.sin(t * 3)))
            if p > 0.15:
                hap(d, 70 + 8 * math.sin(t * 9), 290, ["Sence", "ne?"], [KREM, KIRMIZI], [CIZ, (255, 255, 255)], 60)
            geri_sayim(d, sure - t, 820, 480)
        if cevap:
            em = b["cevap"][2]
            for q, ch in enumerate(em):
                a = min(1, max(0, (t - 0.15 - q * 0.3) / 0.35))
                if a > 0:
                    koy(im, ch, 840 - q * 230, 560 + 10 * math.sin(T * 3 + q), 260 * a * (1 + 0.2 * math.sin(a * math.pi)))
            hap(d, 70, 290, ["CEVAP"], [SARI], [CIZ], 60)
        if son:
            hap(d, 70, 290, ["Bildin", "mi?"], [KREM, SARI], [CIZ, CIZ], 80)
            koy(im, "💬", 860, 560 + 12 * math.sin(T * 3), 200)
        ust_baslik(d, b["baslik"], etk, no, gece=i <= n)
        altyazi(d, metin, t, sure)
        im = son_islem(im, T, t, aydinlik=0.4)
        fligran(im)
        if cevap and t < 0.18:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.6 * (1 - t / 0.18))
        d = ImageDraw.Draw(im)
        alt_panel(d, buyuk, t, f"KAYIT · {b['baslik'].upper()}", satirlar(i, t), no)
        return bitir(im, T, t, sars=6 * math.sin(t * 60) * (1 - t / 0.3) if cevap and t < 0.3 else 0)

    def olaylar(bas, s):
        o = [(bas[j] + 0.25, "pop") for j in range(n)]
        o += [(bas[n] + 0.1, "vurus")] + [(bas[n] + s[n] - 5.2 + j, "tik") for j in range(5)]
        o += [(bas[n + 1] + 0.05, "ding"), (bas[n + 1] + 0.3, "boing"), (bas[n + 2] + 0.2, "pop")]
        return o

    return SAHNE, cerceve, olaylar


d_olc = ImageDraw.Draw(Image.new("RGB", (10, 10)))

if __name__ == "__main__":
    os.makedirs("stok", exist_ok=True)
    for a in sys.argv[1:]:
        no = int(a)
        SAHNE, cerceve, olaylar = hazirla(no)
        if os.environ.get("KARE"):  # hızlı kontrol: her sahneden bir kare
            from motor import sure_al
            for i in range(len(SAHNE)):
                cerceve(i, 2.2 if SAHNE[i][0] != "soru" else 6.0, 8.0, 3.0 + i, None, None).save(f"stok/k{no:02d}_{i}.png")
            continue
        uret(f"y{no:02d}", SAHNE, cerceve, olaylar, f"stok/bilmece{no:02d}.mp4", ekler={"soru": 5.3, "cevap": 1.0})
