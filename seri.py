"""Haftalık "Part 1 / Part 2" dizisi üretir.

Takvim:  Pzt, Sal, Çar -> her gün 3 YENİ filmin Part 1'i
         Per, Cum, Cmt -> sırasıyla Pzt, Sal, Çar filmlerinin Part 2'si
         Paz           -> boş (istenirse en çok izlenenin tekrarı)
Her part 40-80 sn; kesim noktası, sahne geçişlerinden "en heyecanlı" olana konur
(kesimden hemen önce ve sonra ses yüksek, kesmeler sık) ki izleyen "ne oluyor?" desin.

Kullanım:
    python seri.py --kutuphane filmler.json --hafta-basi 2026-11-09 --cikti hafta1/ [--sadece-gun 0]
"""
import argparse, datetime as dt, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from highlight import analiz, render  # noqa: E402
import anlatici  # noqa: E402

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def buyuk(m):
    return m.replace("i", "İ").upper()


def ort(rms, a, b):
    a, b = max(int(a), 0), min(int(b), len(rms))
    return sum(rms[a:b]) / max(b - a, 1)


def partlar(cuts, rms, son, adet=2, en_az=40, en_fazla=80):
    """Filmin başından itibaren `adet` part; her bitiş en gerilimli sahne geçişinde."""
    bas = next((c for c in cuts if c > 3), 0.0)
    sonuc = []
    for _ in range(adet):
        adaylar = [c for c in cuts if bas + en_az <= c <= min(bas + en_fazla, son)]
        if not adaylar:
            bit = min(bas + en_fazla, son)
        else:
            def gerilim(e):
                yogun = sum(1 for x in cuts if e - 8 < x < e) / 8
                return ort(rms, e - 5, e) + ort(rms, e, e + 5) + 40 * yogun
            bit = max(adaylar, key=gerilim)
        sonuc.append((round(bas, 2), round(bit, 2)))
        if bit >= son - 1:
            break
        bas = bit
    return sonuc


def takvim(filmler, hafta_basi):
    """9 filmi haftaya yerleştirir: [(tarih, film, part_no), ...]"""
    t0 = dt.date.fromisoformat(hafta_basi)
    plan = []
    for g in range(3):
        for f in filmler[g * 3:(g + 1) * 3]:
            plan.append((t0 + dt.timedelta(days=g), f, 1))
            plan.append((t0 + dt.timedelta(days=g + 3), f, 2))
    return sorted(plan, key=lambda x: (x[0], filmler.index(x[1])))


def aciklama(f, no, toplam):
    kanca = f["kancalar"][no - 1]
    devam = f"Part {no + 1} {GUNLER[(f['_gun'] + 3) % 7]} günü profilde 👉 Takipte kal!" if no < toplam \
        else "Sence sonu nasıl? Yorumlara yaz 👇"
    return (f"{kanca}\n\n{devam}\n\n🎬 \"{f['ad']}\" ({f['yil']}) © Blender Foundation | studio.blender.org\n"
            f"Lisans: CC BY {f['lisans']}\n\n#animasyon #kısafilm #{f['etiket']} #part{no} #devamıgelecek "
            "#animation #shortfilm #reels")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kutuphane", required=True)
    p.add_argument("--hafta-basi", required=True, help="pazartesi tarihi, YYYY-AA-GG")
    p.add_argument("--hafta", type=int, default=1, help="kaçıncı hafta (kütüphanedeki 9'lu grup)")
    p.add_argument("--cikti", required=True)
    p.add_argument("--sadece-gun", type=int, help="yalnızca bu günü render et (0=Pzt, 6=Paz)")
    p.add_argument("--ses", help="anlatıcı sesi (boşsa anlatıcı eklenmez)")
    p.add_argument("--sadece-plan", action="store_true", help="kesim noktalarını bul, render etme")
    a = p.parse_args()

    kut = json.loads(Path(a.kutuphane).read_text(encoding="utf-8"))
    filmler = kut["filmler"][(a.hafta - 1) * 9:a.hafta * 9]
    for i, f in enumerate(filmler):
        f["_gun"] = i // 3
    out = Path(a.cikti); out.mkdir(parents=True, exist_ok=True)

    onbellek = out / "kesimler.json"  # analiz uzun sürer, bir kere yap
    kes = json.loads(onbellek.read_text()) if onbellek.exists() else {}
    for f in filmler:
        if f["etiket"] not in kes:
            cuts, rms = analiz(f["dosya"])
            kes[f["etiket"]] = partlar(cuts, rms, f.get("jenerik") or len(rms) * 0.85)
            onbellek.write_text(json.dumps(kes, indent=1))
        f["_partlar"] = kes[f["etiket"]]
        print(f["ad"], f["_partlar"])
    if a.sadece_plan:
        return

    kayit = []
    for tarih, f, no in takvim(filmler, a.hafta_basi):
        if no > len(f["_partlar"]):
            continue
        bas, bit = f["_partlar"][no - 1]
        gun = (tarih - dt.date.fromisoformat(a.hafta_basi)).days
        dosya = out / f"{tarih}_{f['etiket']}_part{no}.mp4"
        son = len(f["_partlar"])
        kayit.append({"tarih": str(tarih), "gun": GUNLER[gun], "film": f["ad"], "part": no,
                      "bas": bas, "bit": bit, "dosya": dosya.name,
                      "aciklama": aciklama(f, no, son), "paylasildi": False})
        if a.sadece_gun is not None and gun != a.sadece_gun:
            continue
        hedef = str(dosya).replace(".mp4", "_ham.mp4")  # anlatıcısız hali saklanır, ses değişirse yeniden kullanılır
        render(f["dosya"], hedef, bas, bit, f"{f['ad']} - Part {no}", f["kancalar"][no - 1],
               f"{f['ad']} · Blender Foundation · CC BY {f['lisans']}",
               son_yazi=f"PART {no + 1} {buyuk(GUNLER[(gun + 3) % 7])}" if no < son else "", fade=no >= son,
               altyazi=f.get("altyazi"))
        if f.get("anlatim") and a.ses:
            anlatici.ekle(hedef, f["anlatim"][no - 1], str(dosya), a.ses)
        else:
            import shutil; shutil.copy(hedef, dosya)
        print(f"{tarih} {GUNLER[gun]}: {f['ad']} Part {no} ({bas}-{bit} sn) -> {dosya}")
    # Pazar Özel: kısa filmin tamamı tek videoda
    for pz in kut.get("pazar", [])[a.hafta - 1:a.hafta]:
        tarih = dt.date.fromisoformat(a.hafta_basi) + dt.timedelta(days=6)
        dosya = out / f"{tarih}_{pz['etiket']}_pazar.mp4"
        kayit.append({"tarih": str(tarih), "gun": "Pazar", "film": pz["ad"], "part": 0, "bas": pz["bas"],
                      "bit": pz["bit"], "dosya": dosya.name, "paylasildi": False,
                      "aciklama": f"PAZAR ÖZEL 🍿 Tek partta komple film!\n\n{pz['kanca']}\n\nBu haftanın en iyi filmi "
                                  f"hangisiydi? Yorumlara yaz 👇\n\n🎬 \"{pz['ad']}\" ({pz['yil']}) © Blender Foundation"
                                  f" | studio.blender.org\nLisans: CC BY {pz['lisans']}\n\n#pazarözel #animasyon "
                                  "#kısafilm #animation #shortfilm #reels"})
        if a.sadece_gun in (None, 6):
            render(pz["dosya"], str(dosya), pz["bas"], pz["bit"], f"PAZAR ÖZEL: {pz['ad']}", pz["kanca"],
                   f"{pz['ad']} · Blender Foundation · CC BY {pz['lisans']}")
            print(f"{tarih} Pazar: {pz['ad']} -> {dosya}")
    (out / "takvim.json").write_text(json.dumps(kayit, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
