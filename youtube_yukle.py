"""YouTube'a otomatik yükleme: python3 youtube_yukle.py youtube/takvim.json
Takvimde zamanı önümüzdeki 3 gün içinde olan ve yüklenmemiş videoları yükler,
YouTube'da o saate zamanlar (publishAt). DENEME=1 ise sadece listeler.
Gizli anahtarlar: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (GitHub Secrets)."""
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

TR = timezone(timedelta(hours=3))

def istek(url, veri=None, basliklar={}, yontem=None):
    r = urllib.request.Request(url, data=veri, headers=basliklar, method=yontem)
    with urllib.request.urlopen(r, timeout=600) as c:
        return c.headers, c.read()

def erisim_anahtari():
    veri = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    return json.loads(istek("https://oauth2.googleapis.com/token", veri)[1])["access_token"]

def dosya_al(yol):
    if yol.startswith("http"):  # büyük videolar GitHub Release'ten
        yerel = "/tmp/" + yol.rsplit("/", 1)[1]
        urllib.request.urlretrieve(yol, yerel)
        return yerel
    return yol

def yukle(anahtar, v):
    zaman = datetime.fromisoformat(v["zaman"]).replace(tzinfo=TR)
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if not v.get("gizli") and zaman > datetime.now(TR) + timedelta(minutes=20):
        status["publishAt"] = zaman.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    govde = json.dumps({"snippet": {"title": v["baslik"][:100], "description": v["aciklama"],
                                    "tags": v.get("etiketler", []), "categoryId": "24", "defaultLanguage": "tr"},
                        "status": status}).encode()
    yol = dosya_al(v["dosya"]); boy = os.path.getsize(yol)
    h = {"Authorization": f"Bearer {anahtar}", "Content-Type": "application/json; charset=UTF-8",
         "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(boy)}
    yer = istek("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", govde, h)[0]["Location"]
    with open(yol, "rb") as f:
        vid = json.loads(istek(yer, f.read(), {"Authorization": f"Bearer {anahtar}", "Content-Type": "video/mp4"}, "PUT")[1])["id"]
    if v.get("kapak"):  # sadece uzun videolarda işe yarar
        try:
            istek(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}", open(v["kapak"], "rb").read(),
                  {"Authorization": f"Bearer {anahtar}", "Content-Type": "image/png"})
        except Exception as e:
            print("Kapak eklenemedi:", e)
    return vid, status.get("publishAt", "gizli")

def main():
    yol = sys.argv[1]; takvim = json.load(open(yol, encoding="utf-8"))
    sinir = datetime.now(TR) + timedelta(days=3)
    sira = [v for v in takvim if not v.get("youtube_id") and datetime.fromisoformat(v["zaman"]).replace(tzinfo=TR) <= sinir]
    if not sira: print("Yüklenecek video yok."); return
    if os.environ.get("DENEME"):
        for v in sira: print("DENEME, yüklenecek:", v["zaman"], v["baslik"])
        return
    anahtar = erisim_anahtari()
    for v in sira[:5]:  # günlük kota ~6 yükleme
        vid, ne_zaman = yukle(anahtar, v)
        v["youtube_id"] = vid
        print(f"Yüklendi: {v['baslik']} -> https://youtu.be/{vid} ({ne_zaman})")
        json.dump(takvim, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

main()
