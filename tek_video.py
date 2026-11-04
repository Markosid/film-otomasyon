"""Takvimdeki tek bir videoyu üretir (gerekirse filmi archive.org'dan indirir).

python tek_video.py takvim.json <sıra_no> cikti_klasoru   -> üretilen dosyanın yolunu yazar
"""
import json, os, subprocess, sys, urllib.request
from pathlib import Path

KOK = Path(__file__).parent
sys.path.insert(0, str(KOK))
from highlight import render  # noqa: E402
from seri import GUNLER, buyuk  # noqa: E402
import anlatici  # noqa: E402


def indir(f):
    yol = KOK / f["dosya"]
    if not yol.exists():
        yol.parent.mkdir(parents=True, exist_ok=True)
        print("indiriliyor:", f["url"], flush=True)
        subprocess.run(["curl", "-sSL", "--retry", "3", "-o", str(yol), f["url"]], check=True)
    return str(yol)


def uret(takvim, i, cikti):
    k = takvim[i]
    kut = json.loads((KOK / "kutuphane.json").read_text(encoding="utf-8"))
    f = {x["etiket"]: x for x in kut["filmler"] + kut["pazar"]}[k["etiket"]]
    film = indir(f)
    out = Path(cikti); out.mkdir(parents=True, exist_ok=True)
    hedef = out / k["dosya"]
    kredi = f"{f['ad']} · Blender Foundation · CC BY {f['lisans']}"
    if k["part"] == 0:  # Pazar özel
        render(film, str(hedef), k["bas"], k["bit"], f"PAZAR ÖZEL: {f['ad']}", f["kanca"], kredi)
        return hedef
    no = k["part"]
    son = max(x["part"] for x in takvim if x["etiket"] == k["etiket"])
    gun = GUNLER.index(k["gun"])
    ham = out / k["dosya"].replace(".mp4", "_ham.mp4")
    altyazi = str(KOK / f["altyazi"]) if f.get("altyazi") else None
    render(film, str(ham), k["bas"], k["bit"], f"{f['ad']} - Part {no}", f["kancalar"][no - 1], kredi,
           son_yazi=f"PART {no + 1} {buyuk(GUNLER[(gun + 3) % 7])}" if no < son else "", fade=no >= son,
           altyazi=altyazi)
    if f.get("anlatim"):
        anlatici.ekle(str(ham), f["anlatim"][no - 1], str(hedef), f.get("ses", "en-US-BrianMultilingualNeural"))
        ham.unlink()
    else:
        ham.replace(hedef)
    return hedef


if __name__ == "__main__":
    t = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(uret(t, int(sys.argv[2]), sys.argv[3]))
