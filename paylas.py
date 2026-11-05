"""Takvimdeki sıradaki videoyu Instagram Reels olarak paylaşır.

GitHub Actions günde 3 kez çalıştırır (12:00, 18:00, 21:00 TR). Her çalışmada bugünün
takviminden henüz paylaşılmamış İLK videoyu paylaşır ve takvime "paylasildi": true yazar.

Gerekli gizli değişkenler (GitHub > Settings > Secrets > Actions):
  IG_TOKEN  : Instagram API (Instagram Login) uzun ömürlü erişim anahtarı
Video o anda üretilir (tek_video.py), GitHub'da "videolar" sürümüne yüklenir ve Instagram
oradan çeker. GITHUB_TOKEN ve GITHUB_REPOSITORY Actions tarafından otomatik verilir.
"""
import datetime as dt, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://graph.instagram.com/v21.0"
KIMLIK = "me"
IG_USER_ID = os.environ.get("IG_USER_ID", "17841416898516422")  # eskisinema.arsivi
TOKEN = os.environ.get("IG_TOKEN", "")
TR = dt.timezone(dt.timedelta(hours=3))


def api_sec():
    """Token Instagram girişinden mi, Facebook (sistem kullanıcısı) girişinden mi? İkisini de dener."""
    global API, KIMLIK
    for taban, kimlik in (("https://graph.instagram.com/v21.0", "me"),
                          ("https://graph.facebook.com/v21.0", IG_USER_ID)):
        url = f"{taban}/{kimlik}?" + urllib.parse.urlencode({"fields": "id,username", "access_token": TOKEN})
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                bilgi = json.load(r)
            API, KIMLIK = taban, bilgi.get("id", kimlik)
            print(f"Instagram hesabı: {bilgi.get('username')} ({taban})", flush=True)
            return
        except urllib.error.HTTPError:
            continue
    sys.exit("Token geçersiz: Instagram'a bağlanılamadı (IG_TOKEN'ı kontrol et).")


def istek(yol, veri=None, yontem="GET"):
    veri = dict(veri or {}, access_token=TOKEN)
    url = f"{API}/{yol}"
    if yontem == "GET":
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(veri))
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(veri).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Instagram hatası {e.code}: {e.read().decode()[:500]}")


def paylas(video_url, aciklama, deneme=4):
    for n in range(1, deneme + 1):  # Instagram videoyu bazen çekemiyor (ör. 2207077); birkaç kez dene
        kap = istek(f"{KIMLIK}/media", {"media_type": "REELS", "video_url": video_url, "caption": aciklama,
                                 "share_to_feed": "true"}, "POST")["id"]
        for _ in range(60):  # Instagram videoyu işlerken bekle (en fazla ~10 dk)
            durum = istek(kap, {"fields": "status_code,status"})
            if durum.get("status_code") in ("FINISHED", "ERROR"):
                break
            time.sleep(10)
        if durum.get("status_code") == "FINISHED":
            return istek(f"{KIMLIK}/media_publish", {"creation_id": kap}, "POST")["id"]
        print(f"Deneme {n}: video işlenemedi: {durum}", flush=True)
        time.sleep(60)
    sys.exit("Video Instagram tarafından işlenemedi")


def hikaye_uret(dosya):
    """Reels videosunun ilk 15 sn'si + "YENİ PART PROFİLDE" bandı (hikâye için)."""
    from highlight import FONT
    hedef = dosya.with_name(dosya.stem + "_hikaye.mp4")
    vf = (f"drawtext=fontfile={FONT}:text='YENİ PART PROFİLDE':fontsize=70:fontcolor=white:box=1:"
          "boxcolor=red@0.85:boxborderw=24:x=(w-tw)/2:y=170")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dosya), "-t", "15", "-vf", vf,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(hedef)], check=True)
    return hedef


def hikaye_paylas(video_url):
    kap = istek(f"{KIMLIK}/media", {"media_type": "STORIES", "video_url": video_url}, "POST")["id"]
    for _ in range(40):
        durum = istek(kap, {"fields": "status_code,status"})
        if durum.get("status_code") == "FINISHED":
            return istek(f"{KIMLIK}/media_publish", {"creation_id": kap}, "POST")["id"]
        if durum.get("status_code") == "ERROR":
            sys.exit(f"Hikâye işlenemedi: {durum}")
        time.sleep(10)
    sys.exit("Hikâye zamanında işlenmedi")


def yukle(dosya):
    """Videoyu GitHub'daki 'videolar' sürümüne yükler, herkese açık adresini döner."""
    repo = os.environ["GITHUB_REPOSITORY"]
    if subprocess.run(["gh", "release", "view", "videolar"], capture_output=True).returncode:
        subprocess.run(["gh", "release", "create", "videolar", "--title", "Videolar",
                        "--notes", "Paylaşım için otomatik yüklenen videolar"], check=True)
    subprocess.run(["gh", "release", "upload", "videolar", str(dosya), "--clobber"], check=True)
    return f"https://github.com/{repo}/releases/download/videolar/{urllib.parse.quote(dosya.name)}"


def main():
    takvim_yolu = Path(sys.argv[1] if len(sys.argv) > 1 else "takvim.json")
    takvim = json.loads(takvim_yolu.read_text(encoding="utf-8"))
    bugun = os.environ.get("TARIH") or dt.datetime.now(TR).date().isoformat()
    sira = [i for i, k in enumerate(takvim) if k["tarih"] == bugun and not k["paylasildi"]]
    if not sira:
        print(f"{bugun}: paylaşılacak video yok."); return
    i = sira[0]; k = takvim[i]
    from tek_video import uret
    dosya = uret(takvim, i, "cikti")
    print("Üretildi:", dosya, flush=True)
    hikaye = hikaye_uret(dosya)
    print("Hikâye üretildi:", hikaye, flush=True)
    if os.environ.get("DENEME"):
        if TOKEN:
            api_sec()  # token çalışıyor mu kontrol et
        print("DENEME modu: yüklenmedi ve paylaşılmadı."); return
    api_sec()
    url = yukle(dosya)
    medya = paylas(url, k["aciklama"])
    k["paylasildi"] = True
    k["medya_id"] = medya
    k["paylasim_zamani"] = dt.datetime.now(TR).isoformat(timespec="minutes")
    takvim_yolu.write_text(json.dumps(takvim, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Paylaşıldı: {k['film']} Part {k['part']} -> {medya}", flush=True)
    try:  # hikâye başarısız olsa da Reels paylaşımı geçerli kalır
        k["hikaye_id"] = hikaye_paylas(yukle(hikaye))
        takvim_yolu.write_text(json.dumps(takvim, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Hikâye paylaşıldı:", k["hikaye_id"])
    except (SystemExit, Exception) as e:
        print("Hikâye paylaşılamadı:", e)


if __name__ == "__main__":
    main()
