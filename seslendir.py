"""Takvimdeki her videoya filme atanmış sesle Türkçe anlatıcı ekler (_ham.mp4 -> .mp4)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import anlatici
kut = {f["ad"]: f for f in json.load(open(sys.argv[1]))["filmler"]}
klasor = Path(sys.argv[2])
for k in json.load(open(klasor / "takvim.json")):
    f = kut.get(k["film"])
    ham = klasor / k["dosya"].replace(".mp4", "_ham.mp4")
    if f and f.get("anlatim") and ham.exists():
        anlatici.ekle(str(ham), f["anlatim"][k["part"] - 1], str(klasor / k["dosya"]), f.get("ses", "en-US-BrianMultilingualNeural"))
        print("ses eklendi:", k["dosya"], f.get("ses"))
