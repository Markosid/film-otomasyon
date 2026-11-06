"""Hazır bilmece kalıbı: bilmeceler.py'deki veriden video üretir.
Kullanım: python3 kalip.py 1 [2 3 ...]   (çıktı: stok/bilmece01.mp4)"""
import math, os, re, sys
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
KANCA = ["%90'ı bilemedi!", "Sadece dahiler bilir", "Sonuna kadar izle!", "Herkes yanlış biliyor", "5 saniyede çöz!", "Bunu çözen yok!"]
ARAC = {"🚌", "🚚", "🚆", "✈️", "🚲", "🚒"}
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
    "sofor": dict(govde=(70, 110, 80), kep=(60, 110, 190)),
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


def m_dusunce(d, T):
    d.rectangle([0, 0, W, SAH], fill=(34, 26, 52))
    for j in range(14):
        a = T * 0.4 + j * 0.9
        x, y = 540 + math.cos(a) * (200 + j * 30), 600 + math.sin(a * 1.3) * (180 + j * 18)
        d.text((x, y), "?", font=KALIN(60 + (j % 4) * 30), fill=(60 + j * 3, 46, 90), anchor="mm")
    d.ellipse([60, ZEMIN_Y - 80, 760, ZEMIN_Y + 70], fill=(70, 60, 100))
    d.rectangle([0, ZEMIN_Y - 10, W, SAH], fill=(24, 18, 36))
    d.ellipse([60, ZEMIN_Y - 60, 760, ZEMIN_Y + 50], fill=(80, 70, 115))


def m_patlama(d, T):
    d.rectangle([0, 0, W, SAH], fill=(250, 190, 60))
    for j in range(16):
        a = T * 0.5 + j * math.pi / 8
        d.polygon([(540, 620), (540 + math.cos(a) * 1600, 620 + math.sin(a) * 1600),
                   (540 + math.cos(a + 0.2) * 1600, 620 + math.sin(a + 0.2) * 1600)], fill=(255, 150, 50) if j % 2 else (255, 215, 90))
    d.rectangle([0, ZEMIN_Y - 40, W, SAH], fill=(200, 90, 50))


IKINCI = {"yol": "sokak", "sokak": "yol", "kir": "yol", "mutfak": "oda", "oda": "mutfak", "karanlik": "gece", "gece": "karanlik",
          "sinif": "oda", "hastane": "sokak", "market": "sokak", "nehir": "kir"}
OZEL_MEKAN = {2: ["gece", "sokak"], 9: ["yol", "hastane"], 11: ["oda", "market"], 12: ["sokak", "mutfak"], 15: ["sokak", "mutfak"],
              16: ["sokak", "oda"], 18: ["kir", "nehir"], 13: ["karanlik", "oda"], 28: ["hastane", "oda"]}

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

    mekanlar = OZEL_MEKAN.get(no, [b["mekan"], IKINCI[b["mekan"]]])
    tahmin = None
    m = re.match(r"^(.{1,14}?) m[ıiuü]( dedin)?\?$", b["son"][1])
    if m and not any(x in m.group(1) for x in ("bildin", "düştün", "denedin", "kaçını")):
        tahmin = m.group(1)

    def kisiler_ciz(d, i, t, T, p, sure):
        cevap, son, soru = i == n + 1, i == n + 2, i == n
        konum = []
        for j, (tip, ad) in enumerate(kisiler):
            ozel = dict(TIP[tip]); s = ozel.pop("s", 0.85)
            ana = j == 0
            x, adim, yon = xs[j], 0.0, (1 if j < len(kisiler) - 1 or len(kisiler) == 1 else -1)
            if i == 0 and t < 1.4:  # sahneye yürüyerek girer
                r = 1 - t / 1.4
                x = xs[j] - (r ** 1.6) * (520 + 140 * j) * (1 if yon == 1 else -1)
                adim = T * 9
            y = ZEMIN_Y - abs(math.sin(T * 2.4 + j)) * 5
            if cevap:
                if ana and p > 0.08:
                    y -= abs(math.sin(T * 7)) * 34
                agiz, gz = ("gulen", "buyuk") if ana else ("o", "buyuk")
                el = ("yukari", "yukari") if ana else (("bas", "bas") if t < 1.8 else ("yan", "yukari"))
            elif son:
                y -= abs(math.sin(T * 5 + j)) * 14
                agiz, gz = "gulen", ("kapali" if int(T * 2 + j) % 3 == 0 else "acik")
                el = ("yukari", "yan") if int(T * 3 + j) % 2 else ("yan", "yukari")
            elif soru:
                agiz, gz = "o" if int(T * 1.5 + j) % 2 else "uzgun", "acik"
                el = ("bas", "yan") if int(T * 2 + j) % 2 else ("yan", "bas")
                yon = yon if int(T * 0.8 + j) % 2 else -yon  # sağa sola bakınır
            else:
                konusan = (i % len(kisiler)) == j
                agiz = ("o" if int(T * 6) % 2 else "sirit") if konusan and t > 0.3 else "sirit"
                gz = "acik"
                el = (("ileri", "yan") if int(T * 1.6) % 2 else ("yukari", "yan")) if konusan else ("yan", "yan")
                if not konusan and len(kisiler) > 1:
                    yon = -1 if xs[j] > xs[i % len(kisiler)] else 1  # konuşana bakar
            kisi(d, x, y, s, t=T + j, gozler=gz, agiz=agiz, el=el, yon=yon, adim=adim, **ozel)
            bas_y = y - 370 * s
            etiket(d, x, bas_y - 70, ad, SARI if cevap and ana else KREM, CIZ, 0.8 if len(ad) > 9 else 0.9)
            if soru and ana:  # ter damlası
                f = (T * 1.2) % 1
                dx, dy = x + 60 * s, bas_y + 60 * s + f * 60
                d.polygon([(dx, dy - 22), (dx - 11, dy), (dx + 11, dy)], fill=(120, 190, 255))
                d.ellipse([dx - 11, dy - 10, dx + 11, dy + 12], fill=(120, 190, 255), outline=CIZ, width=2)
            if cevap and not ana and t < 2.2:
                d.text((x + 50, bas_y - 40 - 10 * math.sin(T * 12)), "!", font=KALIN(90), fill=KIRMIZI, anchor="mm")
            konum.append((x, bas_y))
        return konum

    def nesne(im, ch, q, i, t, T, sure, boy=230):
        hx, hy = 860 - q * 220, 560
        a = (t - 0.25 - q * 0.6)
        if a < 0:
            return
        mod = (no + i + q) % 3
        if ch in ARAC:  # araçlar sahnede gezer
            x = W + 150 - (W + 300) * min(1, a / max(1.5, sure - 0.5))
            koy(im, ch, x, hy + 160 + 6 * math.sin(T * 20), boy)
            return
        if mod == 0:  # sağdan uçarak gelir
            r = min(1, a / 0.5)
            x = hx + (1 - r) ** 2 * 500 - math.sin(r * math.pi) * 40
            koy(im, ch, x, hy + 14 * math.sin(T * 2 + q), boy)
        elif mod == 1:  # yukarıdan düşer, zıplar
            r = min(1, a / 0.6)
            y = hy - 600 * (1 - r) ** 2 if r < 1 else hy - abs(math.sin((a - 0.6) * 9)) * 40 * max(0, 1 - (a - 0.6) * 1.5)
            koy(im, ch, hx, y, boy)
        else:  # büyüyerek patlar, sallanır
            r = min(1, a / 0.35)
            koy(im, ch, hx + 10 * math.sin(T * 5), hy, boy * r * (1 + 0.25 * math.sin(r * math.pi)))

    def baloncuk(d, x, y, yazi, t, uzeri_cizik=0.0):
        f = KALIN(50)
        w = max(120, d.textlength(yazi + "?", font=f) + 70)
        for k_, (dx, dy, rr) in enumerate(((-60, 150, 12), (-30, 110, 20))):
            d.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr], fill=KREM, outline=CIZ, width=3)
        d.rounded_rectangle([x - w / 2, y - 45, x + w / 2, y + 55], 40, fill=KREM, outline=CIZ, width=4)
        d.text((x, y + 5), yazi + "?", font=f, fill=CIZ, anchor="mm")
        if uzeri_cizik:
            r = min(1, uzeri_cizik)
            d.line([(x - w / 2, y - 45), (x - w / 2 + w * r, y - 45 + 100 * r)], fill=KIRMIZI, width=14)
            d.line([(x + w / 2, y - 45), (x + w / 2 - w * r, y - 45 + 100 * r)], fill=KIRMIZI, width=14)

    def cerceve(i, t, sure, T, bas, sureler):
        k, metin, buyuk = SAHNE[i]
        p = t / sure
        cevap, son, soru = i == n + 1, i == n + 2, i == n
        sh = Image.new("RGB", (W, SAH), (16, 16, 20))
        d = ImageDraw.Draw(sh)
        if soru:
            m_dusunce(d, T)
        elif cevap:
            m_patlama(d, T)
        else:
            MEKAN[mekanlar[min(i, n) if i < n else 0]](d)
        konum = kisiler_ciz(d, i, t, T, p, sure)
        ax, ay = konum[0]
        if i < n:
            for q, ch in enumerate(hik[i][2]):
                nesne(sh, ch, q, i, t, T, sure)
        if soru:
            soru_isareti(d, 900, 820, 240 + 30 * math.sin(t * 5), abs(math.sin(t * 3)))
            if tahmin and p > 0.3:
                baloncuk(d, min(max(ax + 150, 230), 600), ay - 300, tahmin, t)
            geri_sayim(d, sure - t, 820, 500)
        if cevap:
            if tahmin and t < 1.6:
                baloncuk(d, min(max(ax + 150, 230), 600), ay - 300, tahmin, t, uzeri_cizik=t / 0.4)
            for q, ch in enumerate(b["cevap"][2]):
                a = min(1, max(0, (t - 0.5 - q * 0.3) / 0.35))
                if a > 0:
                    koy(sh, ch, 840 - q * 230, 540 + 12 * math.sin(T * 3 + q), 270 * a * (1 + 0.25 * math.sin(a * math.pi)))
            for c in range(46):  # konfeti
                r_ = (c * 7919) % 1000 / 1000
                cx = (c * 211) % W + 40 * math.sin(T * 3 + c)
                cy = -40 + ((t * (380 + r_ * 300)) + c * 37) % 1400 if t > 0.4 else -100
                renk = (KIRMIZI, SARI, YESIL, (90, 150, 240), KREM)[c % 5]
                d.rectangle([cx, cy, cx + 14, cy + 22], fill=renk)
        if son:
            koy(sh, "💬", 860, 520 + 14 * math.sin(T * 3), 190)
            koy(sh, "👇", 860, 760 + abs(math.sin(T * 6)) * 30, 150)
        # kamera: yavaş yakınlaşma, cevapta vuruş zoom'u, sahne geçişinde kayma
        z = 1 + 0.05 * p
        if cevap and t < 0.5:
            z += 0.14 * (1 - t / 0.5) ** 2
        if z > 1.001:
            cw, ch_ = W / z, SAH / z
            ox, oy = (W - cw) / 2, (SAH - ch_) * 0.62
            sh = sh.crop((int(ox), int(oy), int(ox + cw), int(oy + ch_))).resize((W, SAH), Image.BILINEAR)
        im = Image.new("RGB", (W, H), (16, 16, 20))
        kay = int((1 - t / 0.22) ** 2 * 260) if (t < 0.22 and i > 0) else 0
        im.paste(sh, (kay, 0))
        im.paste(UST_SIYAH, (0, 0), UST)
        d = ImageDraw.Draw(im)
        if i < n and p > 0.12:
            kel = hik[i][3]
            hap(d, 70, 290, kel, [KREM] * (len(kel) - 1) + [KIRMIZI], [CIZ] * (len(kel) - 1) + [(255, 255, 255)], 56)
        if soru and p > 0.1:
            hap(d, 70 + 8 * math.sin(t * 9), 290, ["Sence", "ne?"], [KREM, KIRMIZI], [CIZ, (255, 255, 255)], 60)
        if cevap:
            hap(d, 70, 290 + (1 - min(1, t / 0.3)) * -120, ["CEVAP"], [SARI], [CIZ], 64)
        if son:
            hap(d, 70, 290, ["Bildin", "mi?"], [KREM, SARI], [CIZ, CIZ], 80)
        ust_baslik(d, b["baslik"], etk, no, gece=i <= n)
        d.rectangle([0, SAH - 8, int(W * T / TOPLAM[0]), SAH], fill=KIRMIZI)  # ilerleme çubuğu
        altyazi(d, metin, t, sure)
        im = son_islem(im, T, t, aydinlik=0.4)
        fligran(im)
        if i == 0 and t < 2.0:  # kanca damgası
            yazi = KANCA[no % len(KANCA)]
            r = min(1, t / 0.15)
            boy = int(84 * (2.2 - 1.2 * r))
            kat = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            kd = ImageDraw.Draw(kat)
            f = KALIN(boy)
            w = kd.textlength(yazi, font=f)
            kd.rounded_rectangle([W / 2 - w / 2 - 30, 150 - boy * 0.7, W / 2 + w / 2 + 30, 150 + boy * 0.7], 16, fill=(226, 52, 52, 235), outline=(255, 255, 255, 255), width=6)
            kd.text((W / 2, 150), yazi, font=f, fill=(255, 255, 255, 255), anchor="mm")
            kat = kat.rotate(6 + 2 * math.sin(T * 20), resample=Image.BICUBIC)
            if t > 1.7:
                kat.putalpha(kat.getchannel("A").point(lambda v: int(v * (2.0 - t) / 0.3)))
            im.paste(kat, (0, 470), kat)
        if cevap and t < 0.18:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.6 * (1 - t / 0.18))
        d = ImageDraw.Draw(im)
        alt_panel(d, buyuk, t, f"KAYIT · {b['baslik'].upper()}", satirlar(i, t), no)
        return bitir(im, T, t, sars=8 * math.sin(t * 60) * (1 - t / 0.35) if cevap and t < 0.35 else 0)

    TOPLAM = [60.0]

    def olaylar(bas, s):
        TOPLAM[0] = sum(s)
        o = [(0.2, "whoosh")] + [(bas[j] + 0.3, "pop") for j in range(n)] + [(bas[j] + 0.05, "whoosh") for j in range(1, n + 1)]
        o += [(bas[n] + 0.1, "vurus")] + [(bas[n] + s[n] - 5.2 + j, "tik") for j in range(5)]
        o += [(bas[n + 1] + 0.05, "ding"), (bas[n + 1] + 0.12, "kagit"), (bas[n + 1] + 0.5, "boing"), (bas[n + 2] + 0.2, "pop")]
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
                cerceve(i, float(os.environ.get("KARE")), 8.0, 3.0 + i, None, None).save(f"stok/k{no:02d}_{i}.png")
            continue
        os.environ.setdefault("HIZ", "+12%"); os.environ.setdefault("ARA", "0.2")
        uret(f"y{no:02d}", SAHNE, cerceve, olaylar, f"stok/bilmece{no:02d}.mp4", ekler={"soru": 5.3, "cevap": 1.0})
