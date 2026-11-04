# film-otomasyon

Instagram sayfası için otomatik kısa film / animasyon paylaşımı.

**Takvim:** Pzt-Sal-Çar her gün 3 yeni filmin Part 1'i, Per-Cum-Cmt aynı filmlerin Part 2'si,
Pazar "Pazar Özel" (kısa filmin tamamı). Günde 3 paylaşım: 12:00, 18:00, 21:00 (TR).

**Nasıl çalışır:** GitHub Actions (`.github/workflows/paylas.yml`) her paylaşım saatinde
`takvim.json`'daki sıradaki videoyu `tek_video.py` ile üretir (film archive.org'dan indirilir,
heyecanlı yerde kesilir, Türkçe altyazı ve anlatıcı eklenir), "videolar" sürümüne yükler ve
Instagram API ile Reels olarak paylaşır.

**Kurulum:** Settings > Secrets and variables > Actions > `IG_TOKEN` (Instagram erişim anahtarı).

**Deneme:** Actions > "Instagram paylaşımı" > Run workflow (deneme işaretli): video üretilir,
paylaşılmaz, indirilebilir dosya olarak eklenir.

**Yeni hafta:** `python seri.py --kutuphane kutuphane.json --hafta 2 --hafta-basi 2026-11-16 --cikti hafta2 --sadece-plan`

**Lisans:** Tüm filmler Blender Foundation açık filmleri (CC BY); her açıklamada kaynak belirtilir.
