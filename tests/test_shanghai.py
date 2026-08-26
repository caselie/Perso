from app.games.shanghai import Shanghai
from app.throws import double, miss, single, triple


def jouer(game, *darts):
    for dart in darts:
        game.throw(dart)
    return game


def test_seul_le_numero_du_tour_compte():
    g = jouer(Shanghai(["A"]), triple(20), single(1), single(1))
    assert g.scores[0] == 2


def test_la_cible_suit_le_tour():
    g = Shanghai(["A", "B"])
    assert g.target == 1
    jouer(g, miss(), miss(), miss())  # A
    assert g.target == 1  # toujours le tour 1, c'est à B
    jouer(g, miss(), miss(), miss())  # B
    assert g.target == 2


def test_shanghai_gagne_immediatement():
    g = jouer(Shanghai(["A", "B"]), single(1), double(1), triple(1))
    assert g.finished and g.winner == 0
    assert g.last_turn.note == "SHANGHAI !"


def test_shanghai_desactivable():
    g = jouer(
        Shanghai(["A", "B"], {"shanghai_wins": False}), single(1), double(1), triple(1)
    )
    assert not g.finished
    assert g.scores[0] == 6


def test_le_meilleur_total_gagne_a_la_fin():
    g = Shanghai(["A", "B"], {"rounds": 2, "shanghai_wins": False})
    jouer(g, triple(1), miss(), miss())  # A tour 1 : 3
    jouer(g, single(1), miss(), miss())  # B tour 1 : 1
    jouer(g, miss(), miss(), miss())  # A tour 2 : 0
    jouer(g, triple(2), triple(2), miss())  # B tour 2 : 12
    assert g.finished and g.winner == 1
    assert g.scores == [3, 13]


def test_numero_de_depart_personnalise():
    g = Shanghai(["A"], {"start": 15})
    assert g.target == 15


def test_la_serie_reboucle_apres_le_20():
    g = Shanghai(["A"], {"start": 19, "rounds": 4})
    assert g.target == 19
    jouer(g, miss(), miss(), miss())
    jouer(g, miss(), miss(), miss())
    assert g.target == 1  # 19, 20, puis retour au 1
