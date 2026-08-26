import pytest

from app.throws import BULL, InvalidThrow, Throw, double, miss, single, triple


def test_valeurs():
    assert triple(20).value == 60
    assert double(16).value == 32
    assert single(BULL).value == 25
    assert double(BULL).value == 50
    assert miss().value == 0


def test_labels():
    assert triple(19).label == "T19"
    assert double(1).label == "D1"
    assert single(5).label == "S5"
    assert double(BULL).label == "50"
    assert single(BULL).label == "25"


def test_le_bull_na_pas_de_triple():
    with pytest.raises(InvalidThrow):
        triple(BULL)


def test_secteur_inconnu():
    with pytest.raises(InvalidThrow):
        Throw(1, 21)


def test_hors_cible_sans_multiplicateur():
    with pytest.raises(InvalidThrow):
        Throw(2, 0)


def test_le_bulls_eye_compte_comme_un_double():
    assert double(BULL).is_double
    assert not single(BULL).is_double
