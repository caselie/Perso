import pytest

from app.games.base import GameError
from app.games.killer import Killer
from app.throws import double, single, triple


def partie(joueurs=("A", "B"), **options):
    """Partie aux numéros fixés, pour des tests lisibles."""
    g = Killer(list(joueurs), {"seed": 1, **options})
    g.numbers = [20, 19, 18, 17][: len(joueurs)]
    return g


def jouer(game, *darts):
    for dart in darts:
        game.throw(dart)
    return game


def test_les_numeros_sont_distincts_et_stables():
    a = Killer(["A", "B", "C"], {"seed": 42})
    b = Killer(["A", "B", "C"], {"seed": 42})
    assert a.numbers == b.numbers
    assert len(set(a.numbers)) == 3


def test_on_gagne_des_vies_sur_son_numero():
    g = jouer(partie(), double(20))
    assert g.lives[0] == 2 and not g.is_killer(0)


def test_on_devient_killer_au_maximum_de_vies():
    g = jouer(partie(), triple(20))
    assert g.lives[0] == 3 and g.is_killer(0)


def test_un_non_killer_ne_blesse_personne():
    g = jouer(partie(), double(20), triple(19))
    assert g.lives[1] == 0


def test_un_killer_retire_des_vies():
    g = partie()
    g.lives[1], g.armed[1] = 3, True
    jouer(g, triple(20), single(19))
    assert g.lives[1] == 2
    assert g.kills[0] == 1


def test_le_killer_qui_touche_son_numero_perd_des_vies():
    g = jouer(partie(), triple(20), single(20))
    assert g.lives[0] == 2 and not g.is_killer(0)


def test_penalite_desactivable():
    g = jouer(partie(self_penalty=False), triple(20), single(20))
    assert g.lives[0] == 3


def test_elimination_et_victoire():
    g = partie()
    g.lives[1], g.armed[1] = 3, True
    jouer(g, triple(20), triple(19))
    assert 1 in g.eliminated
    assert g.finished and g.winner == 0


def test_un_joueur_a_zero_vie_qui_na_rien_gagne_nest_pas_elimine():
    g = partie(("A", "B", "C"))
    jouer(g, triple(20), single(19), single(18))
    assert not g.eliminated


def test_les_joueurs_elimines_sont_sautes():
    g = partie(("A", "B", "C"))
    for i in (1, 2):
        g.lives[i], g.armed[i] = 1, True
    jouer(g, triple(20), single(19))  # A élimine B
    assert 1 in g.eliminated
    jouer(g, single(1))  # 3e fléchette de A, la main passe ensuite
    assert g.current == 2  # B est sauté


def test_doubles_uniquement():
    g = partie(double_only=True)
    jouer(g, triple(20))
    assert g.lives[0] == 0
    jouer(g, double(20))
    assert g.lives[0] == 2


def test_annulation_restaure_les_vies():
    g = jouer(partie(), triple(20))
    g.undo()
    assert g.lives[0] == 0 and not g.is_killer(0)


def test_killer_refuse_un_seul_joueur():
    with pytest.raises(GameError):
        Killer(["A"])
