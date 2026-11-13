"""TikTok'a sıradaki videoyu paylaşır (Content Posting API, Direct Post).

Kullanım (GitHub Actions içinde):
  python3 tiktok_paylas.py --bagla KOD   # ilk kurulum: TikTok girişinden gelen kodu anahtara çevirir
  python3 tiktok_paylas.py               # zamanı gelen ilk videoyu paylaşır
Gerekli sırlar: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET. Yenileme anahtarı tiktok/token.enc
içinde, TIKTOK_CLIENT_SECRET ile şifreli durur (açık repoda düz metin anahtar yok).
"""
import datetime as dt, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://open.tiktokapis.com/v2"
KLASOR = Path("tiktok")
TAKVIM = KLASOR / "takvim.json"
SIFRELI = KLASOR / "token.enc"
ANAHTAR = os.environ.get("TIKTOK_CLIENT_KEY", "")
SIR = os.environ.get("TIKTOK_CLIENT_SECRET", "")
DONUS = os.environ.get("TIKTOK_DONUS", "https://markosid.github.io/film-otomasyon/tiktok.html")
GIZLILIK = os.environ.get("TIKTOK_GIZLILIK", "SELF_ONLY")  # denetimden sonra PUBLIC_TO_EVERYONE
DENEME = bool(os.environ.get("DENEME"))
TR = dt.timezone(dt.timedelta(hours=3))


def istek(url, veri=None, token=None, form=False):
    basliklar = {}
    if token:
        basliklar["Authorization"] = f"Bearer {token}"
    govde = None
    if veri is not None:
        if form:
            govde = urllib.parse.urlencode(veri).encode()
            basliklar["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            govde = json.dumps(veri).encode()
            basliklar["Content-Type"] = "application/json; charset=UTF-8"
    req = urllib.request.Request(url, data=govde, headers=basliklar, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"TikTok hatası {e.code}: {e.read().decode()[:500]}")


def sifrele(metin):
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", "env:TIKTOK_CLIENT_SECRET",
                    "-out", str(SIFRELI)], input=metin.encode(), check=True)


def coz():
    return subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", "env:TIKTOK_CLIENT_SECRET",
                           "-in", str(SIFRELI)], capture_output=True, check=True).stdout.decode().strip()


def anahtar_al(veri):
    cevap = istek(f"{API}/oauth/token/", dict(veri, client_key=ANAHTAR, client_secret=SIR), form=True)
    if "access_token" not in cevap:
        sys.exit(f"Anahtar alınamadı: {cevap.get('error')} {cevap.get('error_description')}")
    sifrele(cevap["refresh_token"])  # yenileme anahtarı değişebilir, her seferinde sakla
    return cevap["access_token"]


def bagla(kod):
    anahtar_al({"grant_type": "authorization_code", "code": urllib.parse.unquote(kod).strip(), "redirect_uri": DONUS})
    print("TikTok bağlandı, anahtar şifreli olarak kaydedildi.")


def siradaki(takvim):
    simdi = dt.datetime.now(TR).strftime("%Y-%m-%dT%H:%M")
    for k in takvim:
        if not k.get("paylasildi") and k["zaman"] <= simdi:
            return k


def video_hazirla(k):
    kaynak = k["dosya"]
    if kaynak.startswith("http"):
        hedef = Path("cikti") / Path(urllib.parse.urlparse(kaynak).path).name
        hedef.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(kaynak, hedef)
        return hedef
    return Path(kaynak)


def paylas(token, dosya, aciklama):
    bilgi = istek(f"{API}/post/publish/creator_info/query/", {}, token)["data"]
    secenekler = bilgi.get("privacy_level_options", [])
    gizlilik = GIZLILIK if GIZLILIK in secenekler else "SELF_ONLY"
    print(f"Hesap: @{bilgi.get('creator_username')} · görünürlük: {gizlilik}")
    boyut = dosya.stat().st_size
    parca = boyut if boyut <= 64_000_000 else 10_000_000
    adet = 1 if parca == boyut else boyut // parca  # son parça artanı da alır (TikTok kuralı)
    baslat = istek(f"{API}/post/publish/video/init/", {
        "post_info": {"title": aciklama[:2200], "privacy_level": gizlilik,
                      "disable_comment": False, "disable_duet": False, "disable_stitch": False},
        "source_info": {"source": "FILE_UPLOAD", "video_size": boyut, "chunk_size": parca, "total_chunk_count": adet},
    }, token)["data"]
    with open(dosya, "rb") as f:
        for i in range(adet):
            bas = i * parca
            son = boyut - 1 if i == adet - 1 else bas + parca - 1
            f.seek(bas)
            veri = f.read(son - bas + 1)
            req = urllib.request.Request(baslat["upload_url"], data=veri, method="PUT", headers={
                "Content-Type": "video/mp4", "Content-Range": f"bytes {bas}-{son}/{boyut}"})
            urllib.request.urlopen(req, timeout=300).read()
    for _ in range(40):
        time.sleep(15)
        durum = istek(f"{API}/post/publish/status/fetch/", {"publish_id": baslat["publish_id"]}, token)["data"]
        print("Durum:", durum.get("status"))
        if durum.get("status") == "PUBLISH_COMPLETE":
            return baslat["publish_id"]
        if durum.get("status") == "FAILED":
            sys.exit(f"Paylaşım başarısız: {durum.get('fail_reason')}")
    sys.exit("TikTok işlemeyi bitirmedi, sonraki çalışmada tekrar denenmez; elle kontrol et.")


def main():
    if not (ANAHTAR and SIR):
        print("TikTok sırları yok, atlanıyor.")
        return
    if len(sys.argv) > 2 and sys.argv[1] == "--bagla":
        return bagla(sys.argv[2])
    if not SIFRELI.exists():
        print("TikTok henüz bağlanmadı (tiktok/token.enc yok), atlanıyor.")
        return
    takvim = json.loads(TAKVIM.read_text())
    k = siradaki(takvim)
    if not k:
        print("Sırada zamanı gelmiş TikTok videosu yok.")
        return
    dosya = video_hazirla(k)
    print(f"Sıradaki: {dosya} ({k['zaman']})")
    if DENEME:
        print("Deneme: paylaşılmadı.")
        return
    token = anahtar_al({"grant_type": "refresh_token", "refresh_token": coz()})
    k["publish_id"] = paylas(token, dosya, k["aciklama"])
    k["paylasildi"] = True
    k["paylasim_zamani"] = dt.datetime.now(TR).strftime("%Y-%m-%dT%H:%M+03:00")
    TAKVIM.write_text(json.dumps(takvim, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
