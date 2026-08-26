from app.games.cricket import TARGETS, Cricket
from app.throws import double, single, triple


def jouer(game, *darts):
    for dart in darts:
        game.throw(dart)
    return game


def fermer_tout(game, player, sauf=()):
    """Ferme tous les numéros d'un joueur sans passer par les fléchettes."""
    for target in TARGETS:
        if target not in sauf:
            game.marks[player][target] = 3


def test_trois_marques_ferment_un_numero():
    g = jouer(Cricket(["A", "B"]), triple(20))
    assert g.closed(0, 20)
    assert g.scores[0] == 0  # rien au-delà de la fermeture


def test_les_marques_en_trop_rapportent_des_points():
    g = jouer(Cricket(["A", "B"]), triple(20), triple(20))
    assert g.scores[0] == 60


def test_pas_de_points_si_ladversaire_a_ferme():
    g = Cricket(["A", "B"])
    g.marks[1][20] = 3
    jouer(g, triple(20), triple(20))
    assert g.scores[0] == 0  # le 20 est mort


def test_le_bull_compte_double_au_maximum():
    g = jouer(Cricket(["A", "B"]), double(25), double(25))
    assert g.marks[0][25] == 3
    assert g.scores[0] == 25  # une seule marque en trop


def test_cutthroat_donne_les_points_aux_adversaires():
    g = jouer(Cricket(["A", "B", "C"], {"variant": "cutthroat"}), triple(20), triple(20))
    assert g.scores == [0, 60, 60]


def test_cutthroat_epargne_ceux_qui_ont_ferme():
    g = Cricket(["A", "B", "C"], {"variant": "cutthroat"})
    g.marks[1][20] = 3
    jouer(g, triple(20), triple(20))
    assert g.scores == [0, 0, 60]


def test_victoire_standard_demande_tout_ferme_et_lavantage():
    g = Cricket(["A", "B"])
    fermer_tout(g, 0, sauf=(15,))
    g.scores[1] = 100
    jouer(g, triple(15))
    assert g.has_closed_all(0)
    assert not g.finished  # tout fermé mais mené aux points


def test_victoire_standard_quand_lavantage_est_pris():
    g = Cricket(["A", "B"])
    fermer_tout(g, 0, sauf=(15,))
    jouer(g, triple(15))
    assert g.finished and g.winner == 0


def test_victoire_cutthroat_au_score_le_plus_bas():
    g = Cricket(["A", "B"], {"variant": "cutthroat"})
    fermer_tout(g, 0, sauf=(15,))
    g.scores = [40, 10]
    jouer(g, triple(15))
    assert not g.finished  # A a plus de points que B
    g.scores = [10, 40]
    jouer(g, single(15))
    assert g.finished and g.winner == 0


def test_variante_fermeture_ignore_les_points():
    g = Cricket(["A", "B"], {"variant": "fermeture"})
    fermer_tout(g, 0, sauf=(15,))
    g.scores[1] = 999
    jouer(g, triple(15))
    assert g.finished and g.winner == 0
    assert g.scores[0] == 0


def test_partie_close_quand_tous_les_numeros_sont_morts():
    g = Cricket(["A", "B"])
    fermer_tout(g, 1)
    fermer_tout(g, 0, sauf=(15,))
    g.scores = [0, 30]
    jouer(g, triple(15))
    assert g.finished and g.winner == 1  # B mène aux points


def test_mpr():
    g = jouer(Cricket(["A", "B"]), triple(20), triple(20), single(1))
    assert g.stats()[0]["marks"] == 6
    assert g.stats()[0]["mpr"] == 6.0


def test_annulation():
    g = jouer(Cricket(["A", "B"]), triple(20), triple(20))
    g.undo()
    assert g.scores[0] == 0 and g.marks[0][20] == 3
