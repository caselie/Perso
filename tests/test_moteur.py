"""Mécanique commune : rotation des joueurs, tours, annulation, options."""

import pytest

from app.games import GAMES, build, catalogue
from app.games.base import GameError
from app.games.x01 import X01
from app.throws import Throw, miss, single, triple


def test_catalogue_complet():
    slugs = {jeu["slug"] for jeu in catalogue()}
    assert slugs == {"x01", "cricket", "atc", "shanghai", "killer"}
    for jeu in catalogue():
        assert jeu["label"] and jeu["description"]


def test_la_main_passe_toutes_les_trois_flechettes():
    g = build("x01", ["A", "B", "C"])
    for tour, attendu in enumerate([1, 2, 0]):
        for _ in range(3):
            g.throw(miss())
        assert g.current == attendu, f"tour {tour}"
    assert g.round == 2


def test_lhistorique_recalcule_tout():
    g = build("x01", ["A", "B"], {"start": 501})
    darts = [triple(20), single(5), miss(), triple(19), triple(19), single(1)]
    for dart in darts:
        g.throw(dart)
    avant = g.state()

    rejoue = build("x01", ["A", "B"], {"start": 501})
    for dart in darts:
        rejoue.throw(dart)
    assert rejoue.state() == avant


def test_annuler_jusqua_lorigine():
    g = build("cricket", ["A", "B"])
    for dart in (triple(20), triple(19), triple(18), triple(17)):
        g.throw(dart)
    while g.undo():
        pass
    assert g.state() == build("cricket", ["A", "B"]).state()
    assert g.undo() is False


def test_on_ne_lance_plus_apres_la_victoire():
    g = build("x01", ["A"], {"start": 40})
    g.throw(Throw(2, 20))
    with pytest.raises(GameError):
        g.throw(miss())


def test_options_inconnues_ignorees_et_defauts_appliques():
    g = build("x01", ["A"], {"start": 301, "peu_importe": True})
    assert g.options == {"start": 301, "double_out": True, "double_in": False, "legs": 1}


def test_les_options_hors_bornes_sont_ramenees_dans_la_plage():
    assert X01.normalise_options({"legs": 99})["legs"] == 9
    assert X01.normalise_options({"legs": 0})["legs"] == 1


def test_nombre_de_joueurs_verifie():
    with pytest.raises(GameError):
        build("x01", [])
    with pytest.raises(GameError):
        build("cricket", [f"J{i}" for i in range(7)])


def test_jeu_inconnu():
    with pytest.raises(GameError):
        build("petanque", ["A"])


@pytest.mark.parametrize("slug", sorted(GAMES))
def test_letat_est_serialisable_pour_tous_les_jeux(slug):
    import json

    g = build(slug, ["A", "B"])
    for dart in (triple(20), single(25), miss()):
        g.throw(dart)
    etat = json.loads(json.dumps(g.state()))
    assert etat["players"] == ["A", "B"]
    assert len(etat["scoreboard"]) == 2
    assert etat["last_turn"]["name"] == "A"
