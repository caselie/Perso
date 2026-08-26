"""Parcours de bout en bout dans un vrai navigateur.

Ignoré si Playwright ou Chromium ne sont pas installés :
    pip install playwright && playwright install chromium
"""

from __future__ import annotations

import os
import threading
import time
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api", reason="Playwright non installé")
from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from app.server import create_app  # noqa: E402


def _chromium() -> str | None:
    racine = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""))
    if racine.is_dir():
        for chemin in sorted(racine.glob("chromium-*/chrome-linux/chrome")):
            return str(chemin)
    return None


@pytest.fixture()
def borne(tmp_path):
    """Sert l'application sur un port libre, le temps du test."""
    serveur = make_server("127.0.0.1", 0, create_app(tmp_path / "ui.sqlite3"), threaded=True)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    base = f"http://127.0.0.1:{serveur.server_port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(f"{base}/api/bootstrap", timeout=1)
            break
        except OSError:
            time.sleep(0.1)
    yield base
    serveur.shutdown()


@pytest.fixture()
def page(borne):
    os.environ["NO_PROXY"] = "*"
    with sync_playwright() as pw:
        navigateur = pw.chromium.launch(executable_path=_chromium())
        page = navigateur.new_page(viewport={"width": 1366, "height": 768})
        incidents: list[str] = []
        page.on("pageerror", lambda err: incidents.append(str(err)))
        page.on(
            "console",
            lambda msg: incidents.append(msg.text) if msg.type == "error" else None,
        )
        page.goto(borne, wait_until="networkidle")
        yield page
        navigateur.close()
        assert not incidents, f"erreurs navigateur : {incidents}"


def ajouter_joueurs(page, *noms):
    for nom in noms:
        page.fill("#champ-invite", nom)
        page.click("#form-invite button")
        page.wait_for_timeout(120)


def lancer(page, secteur, multiplicateur=1):
    if multiplicateur != 1:
        page.click(f".mult[data-mult='{multiplicateur}']")
    page.click(f".touche[data-secteur='{secteur}']")
    page.wait_for_timeout(150)


def test_partie_x01_de_bout_en_bout(page):
    ajouter_joueurs(page, "Alice", "Bob")
    page.click(".carte-jeu:has-text('501')")
    page.click(".option:has-text('Score de départ') .option-choix button:has-text('101')")
    page.click("#btn-demarrer")
    page.wait_for_selector("#ecran-partie:not([hidden])")

    assert "T17" in page.inner_text("#consigne")  # suggestion de sortie sur 101

    lancer(page, 20, 3)
    assert page.inner_text("#total-volee") == "60"
    lancer(page, 1)
    page.click("#btn-manque")

    page.wait_for_selector("#voile-tour:not([hidden])")
    assert "Alice" in page.inner_text("#voile-resume")
    assert page.inner_text("#voile-joueur") == "Bob"
    page.click("#voile-ok")
    page.wait_for_selector("#voile-tour", state="hidden")

    lancer(page, 17, 3)
    lancer(page, 25, 2)
    page.wait_for_selector("#voile-fin:not([hidden])")
    assert "Bob" in page.inner_text("#fin-titre")
    assert "151.5" in page.inner_text("#fin-stats")  # 101 points en 2 fléchettes


def test_annulation_depuis_le_voile_de_passage(page):
    ajouter_joueurs(page, "Alice", "Bob")
    page.click(".carte-jeu:has-text('501')")
    page.click("#btn-demarrer")
    page.wait_for_selector("#ecran-partie:not([hidden])")

    for _ in range(3):
        lancer(page, 20, 3)
    page.wait_for_selector("#voile-tour:not([hidden])")
    page.click("#voile-annuler")
    page.wait_for_selector("#voile-tour", state="hidden")

    assert page.inner_text(".score-ligne.actif .nom") == "Alice"
    assert page.inner_text(".score-ligne.actif .valeur") == "381"


def test_le_pave_met_en_avant_les_cibles_du_cricket(page):
    ajouter_joueurs(page, "Alice", "Bob")
    page.click(".carte-jeu:has-text('Cricket')")
    page.click("#btn-demarrer")
    page.wait_for_selector("#ecran-partie:not([hidden])")

    cibles = page.eval_on_selector_all(
        ".touche.cible", "noeuds => noeuds.map(n => Number(n.dataset.secteur))"
    )
    assert sorted(cibles) == [15, 16, 17, 18, 19, 20, 25]

    lancer(page, 20, 3)
    marques = page.inner_text(".score-ligne.actif .marques")
    assert marques.split()[0] == "20"  # ordre du tableau : 20 → 15 puis bull
    assert "⊗" in marques  # trois marques : numéro fermé


def test_le_bull_na_pas_de_triple(page):
    ajouter_joueurs(page, "Alice")
    page.click(".carte-jeu:has-text('Around')")
    page.click("#btn-demarrer")
    page.wait_for_selector("#ecran-partie:not([hidden])")

    page.click(".mult[data-mult='3']")
    assert page.locator(".touche[data-secteur='25']").get_attribute("class").find("eteinte") >= 0
    page.click(".touche[data-secteur='25']", force=True)
    page.wait_for_timeout(200)
    assert page.inner_text("#total-volee") == "0"  # la fléchette n'est pas partie


def test_reprise_apres_rechargement(page, borne):
    ajouter_joueurs(page, "Alice", "Bob")
    page.click(".carte-jeu:has-text('Shanghai')")
    page.click("#btn-demarrer")
    page.wait_for_selector("#ecran-partie:not([hidden])")
    lancer(page, 1, 3)

    page.reload(wait_until="networkidle")
    page.wait_for_selector("#ecran-partie:not([hidden])")
    assert page.inner_text(".score-ligne.actif .valeur") == "3"


def test_deux_ecrans_restent_synchronises(borne):
    """La borne et un téléphone branchés sur la même partie voient la même chose."""
    os.environ["NO_PROXY"] = "*"
    with sync_playwright() as pw:
        navigateur = pw.chromium.launch(executable_path=_chromium())
        grand_ecran = navigateur.new_page(viewport={"width": 1366, "height": 768})
        telephone = navigateur.new_page(viewport={"width": 390, "height": 844})

        grand_ecran.goto(borne, wait_until="networkidle")
        ajouter_joueurs(grand_ecran, "Alice", "Bob")
        grand_ecran.click(".carte-jeu:has-text('501')")
        grand_ecran.click("#btn-demarrer")
        grand_ecran.wait_for_selector("#ecran-partie:not([hidden])")

        # le téléphone rejoint la partie en cours
        telephone.goto(borne, wait_until="networkidle")
        telephone.wait_for_selector("#ecran-partie:not([hidden])")

        # saisie côté téléphone, lecture côté grand écran
        lancer(telephone, 20, 3)
        grand_ecran.wait_for_function(
            "() => document.querySelector('.score-ligne.actif .valeur').textContent === '441'",
            timeout=5000,
        )
        # et l'inverse
        lancer(grand_ecran, 19, 3)
        telephone.wait_for_function(
            "() => document.querySelector('.score-ligne.actif .valeur').textContent === '384'",
            timeout=5000,
        )
        navigateur.close()
