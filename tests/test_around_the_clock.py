from app.games.around_the_clock import AroundTheClock
from app.throws import double, single, triple


def jouer(game, *darts):
    for dart in darts:
        game.throw(dart)
    return game


def test_progression_dans_lordre():
    g = jouer(AroundTheClock(["A"]), single(1), single(3), single(2))
    assert g.target_for(0) == 3  # le 3 lancé hors tour ne compte pas


def test_mode_rapide_avance_du_multiplicateur():
    g = jouer(AroundTheClock(["A"], {"mode": "rapide"}), triple(1))
    assert g.target_for(0) == 4


def test_doubles_uniquement():
    g = AroundTheClock(["A"], {"double_only": True})
    jouer(g, single(1))
    assert g.target_for(0) == 1
    jouer(g, double(1))
    assert g.target_for(0) == 2


def test_victoire_sur_le_bull():
    g = AroundTheClock(["A"], {"include_bull": True})
    g.progress[0] = 20  # tout fait sauf le bull
    jouer(g, single(25))
    assert g.finished and g.winner == 0


def test_sans_bull_la_partie_finit_au_20():
    g = AroundTheClock(["A"], {"include_bull": False})
    g.progress[0] = 19
    jouer(g, single(20))
    assert g.finished


def test_taux_de_reussite():
    g = jouer(AroundTheClock(["A"]), single(1), single(5), single(2))
    assert g.stats()[0] == {
        "darts": 3,
        "points": 2,
        "hits": 2,
        "hit_pct": 66.7,
        "average3": 8.0,
    }
