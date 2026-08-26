import pytest

from app.checkout import checkout_route


def libelles(score, darts=3, double_out=True):
    route = checkout_route(score, darts, double_out)
    return [dart.label for dart in route] if route else None


def test_sortie_en_une_flechette():
    assert libelles(40) == ["D20"]
    assert libelles(50) == ["50"]
    assert libelles(2) == ["D1"]


def test_le_chemin_le_plus_court_est_prefere():
    assert libelles(100) == ["T20", "D20"]  # et non trois fléchettes
    assert len(libelles(170)) == 3


@pytest.mark.parametrize("score", [170, 167, 164, 161, 158, 121, 99, 61, 32])
def test_le_chemin_totalise_bien_le_score(score):
    route = checkout_route(score, 3)
    assert route is not None
    assert sum(dart.value for dart in route) == score
    assert route[-1].is_double  # on sort toujours au double


def test_scores_sans_sortie():
    assert libelles(171) is None  # au-dessus du maximum
    assert libelles(1) is None  # injouable au double
    assert libelles(0) is None
    assert libelles(111, darts=2) is None  # 111 demande trois fléchettes


def test_sans_sortie_au_double():
    route = checkout_route(3, 3, double_out=False)
    assert sum(dart.value for dart in route) == 3
    assert libelles(1, double_out=False) == ["S1"]


def test_le_nombre_de_flechettes_est_respecte():
    assert libelles(60, darts=1) is None  # pas de double à 60
    assert libelles(60, darts=2) == ["S20", "D20"]
