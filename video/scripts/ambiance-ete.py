"""Ambiance sonore d'été synthétisée : clapotis, nappe chaude, oiseaux lointains.
    python3 scripts/ambiance-ete.py <sortie.wav> [durée en s]
"""

import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(11)


def passe_bas(x, coupure):
    a = np.exp(-2 * np.pi * coupure / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def clapotis(n):
    # Bruit filtré modulé par des vaguelettes irrégulières.
    bruit = passe_bas(rng.standard_normal(n), 700) - passe_bas(rng.standard_normal(n), 120) * 0.5
    t = np.arange(n) / SR
    houle = 0.55 + 0.45 * np.sin(2 * np.pi * 0.31 * t) * np.sin(2 * np.pi * 0.13 * t + 1)
    gouttes = np.zeros(n)
    for _ in range(int(n / SR * 2.5)):
        d = rng.integers(0, n - 4000)
        f = rng.uniform(600, 1400)
        tt = np.arange(4000) / SR
        gouttes[d : d + 4000] += np.sin(2 * np.pi * f * (1 + 6 * tt) * tt) * np.exp(-tt * 60) * 0.25
    return bruit * houle * 2.2 + gouttes


def nappe(n):
    t = np.arange(n) / SR
    accord = (146.83, 220.0, 277.18, 329.63, 440.0)  # Ré majeur 9, chaud et ouvert
    x = sum(np.sin(2 * np.pi * f * t + i) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + i)) for i, f in enumerate(accord))
    return passe_bas(x, 900) * 0.18


def oiseaux(n):
    x = np.zeros(n)
    for _ in range(int(n / SR * 0.5)):
        d = rng.integers(0, n - SR)
        for k in range(rng.integers(2, 5)):
            tt = np.arange(int(0.09 * SR)) / SR
            f0 = rng.uniform(2800, 4200)
            chant = np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * 22 * tt)) * tt)
            env = np.sin(np.pi * tt / tt[-1]) ** 2
            s = d + int(k * 0.13 * SR)
            x[s : s + len(tt)] += chant * env * 0.08
    return x


if __name__ == "__main__":
    sortie = sys.argv[1]
    duree = float(sys.argv[2]) if len(sys.argv) > 2 else 15
    n = int(duree * SR)
    t = np.arange(n) / SR
    mix = clapotis(n) * 0.5 + nappe(n) + oiseaux(n)
    mix *= np.clip(t / 1.5, 0, 1) * np.clip((duree - t) / 2, 0, 1)
    mix = mix / np.max(np.abs(mix)) * 0.8
    with wave.open(sortie, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("ok", sortie)
