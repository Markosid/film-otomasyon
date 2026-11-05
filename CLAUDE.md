# film-otomasyon: Claude için proje kuralları

Instagram sayfası **@eskisinema.arsivi** için kısa film kliplerini otomatik paylaşan sistem. Ayrıntılar `README.md`'de.

## Kullanıcı
- Kullanıcı Türkçe yazar; her zaman **sade Türkçe** ile cevap ver, teknik terimleri açıkla.
- Günlük Claude kotası sınırlı: işleri toplu yap, gereksiz dosya okuma ve alt ajan kullanma. En küçük çözümü seç (`.claude/skills/ponytail`).

## Telif (kesin kural)
- Sadece ticari kullanıma izin veren açık lisanslı (CC BY / CC0) **renkli, modern** filmler: Blender açık filmleri vb.
- Telifli film, dizi veya müzik asla. Siyah-beyaz eski filmler kullanılmaz.
- Her açıklamada film adı ve lisans/kaynak belirtilir.

## Format
- 9:16 Reels. Part 1 heyecanlı yerde biter, Part 2 devamı; uzun filmler Part 3/4 ile sürer.
- Türkçe altyazı + 3-6 sn Türkçe yapay zekâ anlatıcı girişi. Ses: erkek, rahat ton (kadın başrollü filmlerde kadın ses).
- Video sonunda gün yazısı yok; "Part 2 ... günü" bilgisi sadece açıklamada.
- Günde 3 paylaşım: 12:00, 18:00, 21:00 (TR). Pazar "Pazar Özel" (kısa filmin tamamı).
- Her Reels'ten sonra ilk 15 sn hikâyeye de gider.

## Nasıl çalışır
- `.github/workflows/paylas.yml` yarım saatte bir `paylas.py takvim.json --kontrol` ile sırayı kontrol eder, videoyu `tek_video.py` ile üretip paylaşır, `takvim.json`'u işaretleyip `main`'e push eder.
- Bot `main`'e doğrudan yazıyor: `takvim.json`'u değiştirmeden önce `main`'i çek, çakışma yaratma.
- Yeni hafta planı: `seri.py` (komut README'de). Film listesi: `kutuphane.json`, altyazılar: `subs/`.
- Deneme: Actions > "Instagram paylaşımı" > Run workflow (deneme işaretli), paylaşmaz.

## Güvenlik
- `IG_TOKEN` sadece GitHub Secrets'ta durur. Token'ı asla koda, sohbete veya loga yazma.
- Gerçek paylaşım dışarıya giden bir işlemdir; kullanıcı istemeden elle paylaşım tetikleme.
