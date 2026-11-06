"""Müzik yatağı ve ses efektleri (numpy ile sentez, telifsiz)."""
import numpy as np, wave
SR = 44100
R = np.random.default_rng(7)

def yaz(f, x):
    x = np.clip(x, -1, 1); x = (x * 32767).astype(np.int16)
    with wave.open(f, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.stack([x, x], 1).ravel().tobytes())

def alcak(x, a=0.05):  # basit alçak geçiren filtre
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def pluck(fr, dur=0.6, amp=0.3):  # Karplus-Strong
    n = int(SR / fr); buf = R.uniform(-1, 1, n); out = np.zeros(int(SR * dur))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = 0.996 * 0.5 * (buf[i % n] + buf[(i + 1) % n])
    return out * amp

def pad(fr, dur, amp):  # yumuşak sentez pad
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return amp * env * sum(np.sin(2 * np.pi * fr * m * t + m) / m for m in (1, 2, 3))

def muzik(sure, minor=False):
    x = np.zeros(int(SR * (sure + 2)))
    if minor:
        akor = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 207.7, 246.9]]
        vurus = 0.5
    else:
        akor = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
        vurus = 0.36
    i = 0; t = 0.0
    while t < sure:
        a = akor[(i // 8) % 4]; nota = a[[0, 2, 1, 2][i % 4]] * (2 if i % 8 >= 4 else 1)
        p = pluck(nota, 0.8, 0.14); s = int(t * SR); x[s:s + len(p)] += p[:len(x) - s]
        if i % 8 == 0:
            b = pad(a[0] / 2, vurus * 8, 0.10); x[s:s + len(b)] += b[:len(x) - s]
        t += vurus; i += 1
    return x[:int(SR * sure)]

def efekt(tur):
    t = np.arange(SR * 2) / SR
    if tur == "pop":
        tt = t[:int(SR * .09)]; return 0.5 * np.sin(2 * np.pi * (600 + 2500 * tt) * tt) * np.exp(-tt * 40)
    if tur == "tik":
        tt = t[:int(SR * .05)]; return 0.5 * np.sin(2 * np.pi * 1500 * tt) * np.exp(-tt * 90)
    if tur == "vurus":
        tt = t[:int(SR * .8)]; return 0.9 * np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 10)) * tt) * np.exp(-tt * 4)
    if tur == "ding":
        tt = t[:int(SR * 1.5)]; return 0.32 * (np.sin(2 * np.pi * 1046 * tt) + 0.5 * np.sin(2 * np.pi * 1568 * tt)) * np.exp(-tt * 2.5)
    if tur == "whoosh":
        n = int(SR * 1.0); tt = t[:n]; g = R.uniform(-1, 1, n)
        return 0.5 * (g - alcak(g, 0.3)) * np.sin(np.pi * tt / 1.0) ** 2
    if tur == "fren":
        n = int(SR * 1.3); tt = t[:n]
        cig = np.sin(2 * np.pi * (2400 - 600 * tt) * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * tt))
        g = R.uniform(-1, 1, n) * 0.4
        return 0.28 * (cig + g) * np.minimum(1, tt / 0.05) * np.exp(-tt * 1.6)
    if tur == "boing":
        tt = t[:int(SR * .7)]; f = 300 + 200 * np.exp(-tt * 4) * np.sin(2 * np.pi * 9 * tt)
        return 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3)
    if tur == "horlama":
        n = int(SR * 1.6); tt = t[:n]; g = alcak(R.uniform(-1, 1, n), 0.04) * 5
        return 0.35 * g * np.sin(np.pi * tt / 1.6) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt))
    if tur == "kagit":
        n = int(SR * .25); tt = t[:n]; g = R.uniform(-1, 1, n)
        return 0.25 * (g - alcak(g, 0.5)) * np.exp(-tt * 14)
    return np.zeros(1)

def motor(sure):
    n = int(SR * sure); t = np.arange(n) / SR
    g = alcak(R.uniform(-1, 1, n), 0.02) * 6
    return 0.18 * (g + 0.5 * np.sin(2 * np.pi * 48 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * t)))

def karistir(cikti, sure, olaylar, muzik_ses=0.35, minor=False, motor_bitis=None):
    x = muzik(sure, minor) * muzik_ses
    if motor_bitis:
        m = motor(motor_bitis); m[-SR // 2:] *= np.linspace(1, 0, SR // 2); x[:len(m)] += m
    for zaman, tur in olaylar:
        e = efekt(tur); s = int(zaman * SR)
        if s < len(x): x[s:s + len(e)] += e[:len(x) - s]
    yaz(cikti, x)
