"""Synthétise les bruitages et la musique de la vidéo de présentation.

Tout est généré ici, sans échantillon externe : pas de droits à gérer.
    python3 scripts/synthese-audio.py   (depuis video/, nécessite numpy)
"""

import wave
from pathlib import Path

import numpy as np

SR = 44100
SORTIE = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(7)


def t(duree):
    return np.arange(int(duree * SR)) / SR


def enveloppe(n, attaque=0.003, chute=0.2):
    x = np.arange(n) / SR
    return np.minimum(x / attaque, 1) * np.exp(-x / chute)


def passe_bas(signal, coupure):
    # Filtre RC d'ordre 1, suffisant pour adoucir un bruit.
    a = np.exp(-2 * np.pi * coupure / SR)
    sortie = np.empty_like(signal)
    acc = 0.0
    for i, s in enumerate(signal):
        acc = (1 - a) * s + a * acc
        sortie[i] = acc
    return sortie


def ecrire(nom, signal, gain=0.9):
    signal = signal / (np.max(np.abs(signal)) or 1) * gain
    donnees = (np.clip(signal, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(SORTIE / nom), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(donnees.tobytes())


def impact():
    # « Tchak » : claquement bref + corps grave du sisal.
    x = t(0.35)
    claque = rng.standard_normal(len(x)) * enveloppe(len(x), 0.0005, 0.012)
    corps = np.sin(2 * np.pi * (140 * np.exp(-x * 18) + 60) * x) * enveloppe(len(x), 0.001, 0.07)
    return passe_bas(claque, 5000) * 0.8 + corps


def buzzer():
    x = t(0.7)
    onde = np.sign(np.sin(2 * np.pi * 98 * x)) + np.sign(np.sin(2 * np.pi * 103.5 * x))
    return passe_bas(onde, 1800) * np.minimum(x / 0.01, 1) * np.clip((0.7 - x) / 0.1, 0, 1)


def note(freq, duree, chute):
    x = t(duree)
    tri = 2 * np.abs(2 * ((x * freq) % 1) - 1) - 1
    return (tri + 0.3 * np.sin(2 * np.pi * freq * 2 * x)) * enveloppe(len(x), 0.004, chute)


def victoire():
    notes = [523.25, 659.25, 783.99, 1046.5]
    sortie = np.zeros(int(1.4 * SR))
    for i, f in enumerate(notes):
        debut = int(i * 0.09 * SR)
        n = note(f, 1.4 - i * 0.09, 0.5 if i == 3 else 0.12)
        sortie[debut : debut + len(n)] += n[: len(sortie) - debut]
    return sortie


def boom():
    # Le « 180 » : grosse caisse de cinéma + scintillement aigu.
    x = t(1.6)
    grave = np.sin(2 * np.pi * np.cumsum(150 * np.exp(-x * 4) + 38) / SR) * enveloppe(len(x), 0.002, 0.45)
    souffle = passe_bas(rng.standard_normal(len(x)), 900) * enveloppe(len(x), 0.002, 0.25) * 3
    eclat = sum(note(f, 1.6, 0.35) for f in (1567.98, 2093.0, 2637.0)) * 0.12
    return grave + souffle + eclat


def touche():
    x = t(0.05)
    bruit = rng.standard_normal(len(x))
    return (bruit - passe_bas(bruit, 2500)) * enveloppe(len(x), 0.0003, 0.008)


def musique(duree=24.0, bpm=120):
    # Boucle électro sobre : La m – Fa – Do – Sol, une mesure par accord.
    x = t(duree)
    sortie = np.zeros(len(x))
    temps = 60 / bpm
    progression = [(110.0, (220.0, 261.63, 329.63)), (87.31, (174.61, 220.0, 261.63)),
                   (130.81, (261.63, 329.63, 392.0)), (98.0, (196.0, 246.94, 293.66))]
    kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t(0.4) * 30) + 45) / SR) * enveloppe(int(0.4 * SR), 0.001, 0.12)
    charleston = rng.standard_normal(int(0.06 * SR))
    charleston = (charleston - passe_bas(charleston, 6000)) * enveloppe(len(charleston), 0.0005, 0.015)
    pompe = np.ones(len(x))
    nb_temps = int(duree / temps)
    for b in range(nb_temps):
        d = int(b * temps * SR)
        sortie[d : d + len(kick)] += kick[: len(sortie) - d]
        pompe[d : d + int(0.25 * SR)] = np.linspace(0.25, 1, int(0.25 * SR))[: len(pompe) - d]
        dh = int((b + 0.5) * temps * SR)
        if dh < len(sortie):
            sortie[dh : dh + len(charleston)] += charleston[: len(sortie) - dh] * 0.35
    nappe = np.zeros(len(x))
    for m in range(int(duree / (4 * temps)) + 1):
        basse, accord = progression[m % 4]
        d = int(m * 4 * temps * SR)
        n = int(4 * temps * SR)
        xs = np.arange(min(n, len(x) - d)) / SR
        if len(xs) == 0:
            break
        scie = 2 * ((xs * basse) % 1) - 1
        for k in range(8):  # basse en croches
            seg = (xs >= k * temps / 2) & (xs < (k + 1) * temps / 2)
            nappe[d : d + len(xs)][seg] += scie[seg] * 0.35 * np.exp(-(xs[seg] - k * temps / 2) * 6)
        for f in accord:
            nappe[d : d + len(xs)] += np.sin(2 * np.pi * f * xs) * 0.12 + np.sin(2 * np.pi * f * 2.003 * xs) * 0.03
    sortie += passe_bas(nappe, 1400) * pompe
    fondu = np.clip((duree - x) / 1.5, 0, 1) * np.clip(x / 0.3, 0, 1)
    return sortie * fondu


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    ecrire("impact.wav", impact())
    ecrire("buzzer.wav", buzzer(), 0.7)
    ecrire("victoire.wav", victoire(), 0.8)
    ecrire("boom.wav", boom())
    ecrire("touche.wav", touche(), 0.5)
    ecrire("musique.wav", musique(), 0.8)
    print("ok :", ", ".join(sorted(p.name for p in SORTIE.glob("*.wav"))))
