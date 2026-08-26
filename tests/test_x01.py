from app.games.x01 import X01
from app.throws import double, miss, single, triple


def jouer(game, *darts):
    for dart in darts:
        game.throw(dart)
    return game


def test_decompte_simple():
    g = jouer(X01(["A", "B"], {"start": 501}), triple(20), triple(20), triple(20))
    assert g.scores[0] == 321
    assert g.current == 1  # la main passe après trois fléchettes


def test_bust_si_score_negatif():
    g = jouer(X01(["A"], {"start": 40}), triple(20))
    assert g.scores[0] == 40
    assert g.last_turn.note == "BUST"


def test_bust_si_il_reste_un_point_en_sortie_au_double():
    g = jouer(X01(["A"], {"start": 21}), single(20))
    assert g.scores[0] == 21  # rester à 1 est injouable au double
    assert g.last_turn.note == "BUST"


def test_bust_si_on_atteint_zero_sans_double():
    g = jouer(X01(["A"], {"start": 40}), single(20), single(20))
    assert g.scores[0] == 40
    assert not g.finished


def test_sortie_au_double():
    g = jouer(X01(["A"], {"start": 40}), double(20))
    assert g.finished and g.winner == 0
    assert g.scores[0] == 0


def test_sortie_simple_quand_le_double_nest_pas_impose():
    g = jouer(X01(["A"], {"start": 40, "double_out": False}), single(20), single(20))
    assert g.finished


def test_le_bulls_eye_sort_en_double():
    g = jouer(X01(["A"], {"start": 50}), double(25))
    assert g.finished


def test_entree_au_double():
    g = X01(["A"], {"start": 501, "double_in": True})
    jouer(g, triple(20), single(20))
    assert g.scores[0] == 501  # rien ne compte avant le double
    jouer(g, double(20))
    assert g.scores[0] == 461
    assert g.opened[0]


def test_bust_annule_toute_la_volee():
    g = jouer(X01(["A"], {"start": 100}), triple(20), triple(20))
    assert g.scores[0] == 100  # T20 puis bust : les 60 premiers sont perdus


def test_annulation_rejoue_lhistorique():
    g = jouer(X01(["A", "B"], {"start": 501}), triple(20), triple(20), triple(20))
    assert g.current == 1
    g.undo()
    assert g.current == 0 and g.darts == 2
    assert g.scores[0] == 381


def test_annulation_dune_victoire():
    g = jouer(X01(["A"], {"start": 40}), double(20))
    assert g.finished
    g.undo()
    assert not g.finished and g.scores[0] == 40


def test_manches_multiples_et_alternance_du_lanceur():
    g = X01(["A", "B"], {"start": 40, "legs": 2})
    jouer(g, double(20))
    assert not g.finished
    assert g.legs_won[0] == 1
    assert g.current == 1  # B commence la manche suivante
    assert g.scores == [40, 40]
    jouer(g, double(20))
    assert g.legs_won == [1, 1] and not g.finished
    jouer(g, double(20))  # A entame la 3e manche
    assert g.finished and g.winner == 0


def test_statistiques_moyenne_et_180():
    g = jouer(X01(["A"], {"start": 501}), triple(20), triple(20), triple(20))
    stats = g.stats()[0]
    assert stats["points"] == 180 and stats["darts"] == 3
    assert stats["average3"] == 180.0
    assert stats["count_180"] == 1


def test_la_volee_bustee_compte_zero_dans_la_moyenne():
    g = jouer(X01(["A"], {"start": 100}), triple(20), triple(20), miss())
    stats = g.stats()[0]
    assert stats["points"] == 0 and stats["darts"] == 3
    assert stats["average3"] == 0.0


def test_meilleur_checkout_sur_la_volee_entiere():
    g = jouer(X01(["A"], {"start": 101}), triple(17), double(25))
    assert g.stats()[0]["best_checkout"] == 101
    assert g.stats()[0]["checkout_pct"] == 100.0
