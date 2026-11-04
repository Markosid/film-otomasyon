"""Türkçe anlatıcı sesi üretir: python tts.py "metin" cikti.mp3"""
import asyncio, os, ssl, sys
import edge_tts, edge_tts.communicate as c
if os.path.exists("/root/.ccr/ca-bundle.crt"):  # Claude ortamının proxy sertifikası
    c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
async def main(t, out, ses="tr-TR-AhmetNeural"):
    await edge_tts.Communicate(t, ses, rate="-8%").save(out)
asyncio.run(main(sys.argv[1], sys.argv[2], *(sys.argv[3:4])))
