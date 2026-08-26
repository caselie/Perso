import pytest

from app.server import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(tmp_path / "test.sqlite3")
    app.config.update(TESTING=True)
    with app.test_client() as client:
        client.application = app
        yield client


def joueur(client, nom):
    return client.post("/api/players", json={"name": nom}).get_json()


def lancer(client, multiplier, sector):
    reponse = client.post("/api/match/throw", json={"multiplier": multiplier, "sector": sector})
    return reponse.get_json(), reponse.status_code


def test_page_daccueil_servie(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert b"Borne" in reponse.data


def test_bootstrap(client):
    donnees = client.get("/api/bootstrap").get_json()
    assert {jeu["slug"] for jeu in donnees["games"]} == {"x01", "cricket", "atc", "shanghai", "killer"}
    assert donnees["match"] is None
    assert donnees["players"] == []


def test_creation_de_joueur_idempotente(client):
    a = joueur(client, "Alice")
    assert a["name"] == "Alice"
    assert joueur(client, "  alice ")["id"] == a["id"]
    assert len(client.get("/api/players").get_json()) == 1


def test_nom_vide_refuse(client):
    assert client.post("/api/players", json={"name": "   "}).status_code == 400


def test_partie_complete(client):
    a, b = joueur(client, "Alice"), joueur(client, "Bob")
    etat = client.post(
        "/api/match", json={"game": "x01", "players": [a, b], "options": {"start": 101}}
    ).get_json()
    assert etat["scoreboard"][0]["score"] == 101
    assert etat["seats"][0]["name"] == "Alice"

    etat, _ = lancer(client, 3, 17)
    etat, _ = lancer(client, 2, 25)
    assert etat["finished"] and etat["winner"] == 0
    assert etat["saved"] is True

    parties = client.get("/api/matches").get_json()
    assert parties[0]["winner"] == "Alice"
    assert client.get(f"/api/players/{a['id']}/stats").get_json()["wins"] == 1


def test_flechette_invalide_rejetee(client):
    a = joueur(client, "Alice")
    client.post("/api/match", json={"game": "x01", "players": [a]})
    donnees, code = lancer(client, 3, 25)
    assert code == 400 and "bull" in donnees["error"]


def test_lancer_sans_partie(client):
    donnees, code = lancer(client, 1, 20)
    assert code == 400 and "aucune partie" in donnees["error"]


def test_annulation(client):
    a = joueur(client, "Alice")
    client.post("/api/match", json={"game": "x01", "players": [a], "options": {"start": 501}})
    lancer(client, 3, 20)
    etat = client.post("/api/match/undo").get_json()
    assert etat["scoreboard"][0]["score"] == 501
    assert etat["history_length"] == 0


def test_pas_dannulation_apres_enregistrement(client):
    a = joueur(client, "Alice")
    client.post("/api/match", json={"game": "x01", "players": [a], "options": {"start": 40}})
    lancer(client, 2, 20)
    assert client.post("/api/match/undo").status_code == 400


def test_abandon_efface_la_partie(client):
    a = joueur(client, "Alice")
    client.post("/api/match", json={"game": "x01", "players": [a]})
    assert client.delete("/api/match").status_code == 204
    assert client.get("/api/match").get_json() is None
    assert client.get("/api/matches").get_json() == []


def test_reprise_apres_redemarrage(client, tmp_path):
    a, b = joueur(client, "Alice"), joueur(client, "Bob")
    client.post(
        "/api/match", json={"game": "cricket", "players": [a, b], "options": {"variant": "cutthroat"}}
    )
    lancer(client, 3, 20)
    lancer(client, 3, 20)

    # nouveau serveur sur la même base : la partie doit repartir à l'identique
    redemarre = create_app(client.application.db.path).test_client()
    etat = redemarre.get("/api/match").get_json()
    assert etat["history_length"] == 2
    assert etat["scoreboard"][1]["score"] == 60  # cut-throat : les points vont à Bob
    assert etat["options"]["variant"] == "cutthroat"


def test_le_killer_recoit_des_numeros(client):
    a, b = joueur(client, "Alice"), joueur(client, "Bob")
    etat = client.post("/api/match", json={"game": "killer", "players": [a, b]}).get_json()
    numeros = [ligne["number"] for ligne in etat["scoreboard"]]
    assert len(set(numeros)) == 2
    assert etat["options"]["seed"] > 0


def test_joueur_invite_sans_compte(client):
    etat = client.post(
        "/api/match", json={"game": "atc", "players": [{"name": "Passant"}]}
    ).get_json()
    assert etat["players"] == ["Passant"]
    assert etat["seats"][0]["id"] is None


def test_stats_joueur_inconnu(client):
    assert client.get("/api/players/999/stats").status_code == 404


def test_flechette_mal_formee(client):
    a = joueur(client, "Alice")
    client.post("/api/match", json={"game": "x01", "players": [a]})
    reponse = client.post("/api/match/throw", json={"sector": 20})
    assert reponse.status_code == 400
    assert "multiplier" in reponse.get_json()["error"]
