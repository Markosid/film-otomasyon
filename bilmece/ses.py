"""Anlatıcı: python ses.py "metin" cikti.mp3 [ses] [pitch] [rate]"""
import asyncio, os, ssl, sys
import edge_tts, edge_tts.communicate as c
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
a = sys.argv + [None] * 5
asyncio.run(edge_tts.Communicate(a[1], a[3] or "tr-TR-AhmetNeural", rate=a[5] or "-4%", pitch=a[4] or "-6Hz").save(a[2]))
