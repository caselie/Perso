# Borne de fléchettes

Une borne de comptage pour jeu de fléchettes, dans l'esprit de RaspyDarts, mais
prévue pour tourner sur **un vieux PC portable** plutôt que sur un Raspberry Pi.

Le score se saisit à la main : on touche la zone atteinte (simple / double /
triple + numéro), la borne s'occupe des règles, du décompte, des bust, des
sorties au double, du passage de main et des statistiques. Elle fonctionne donc
avec **n'importe quelle cible**, pointes acier comprises.

```
┌─ Borne (le portable) ────────┐        ┌─ Télécommande (facultatif) ─┐
│  Flask + SQLite  ← http →    │  wifi  │  téléphone, tablette,       │
│  navigateur en plein écran   │ ←────→ │  second écran               │
└──────────────────────────────┘        └─────────────────────────────┘
```

## Démarrage rapide

```bash
git clone <ce dépôt> raspydarts && cd raspydarts
./scripts/run.sh                 # crée le venv, démarre le serveur et le kiosque
```

Sous Windows : double-cliquez sur `scripts\run.bat`.

Pour développer, sans ouvrir de navigateur :

```bash
./scripts/run.sh --serveur       # http://127.0.0.1:8080
```

Le montage physique (cotes de la cible, distribution Linux, démarrage
automatique, saisie sans écran tactile) est décrit dans
[`docs/borne.md`](docs/borne.md).

## Les jeux

| Jeu | Principe | Options |
| --- | --- | --- |
| **501 / 301** | Descendre à zéro pile. | Score de départ (101 → 1001), sortie au double, entrée au double, manches gagnantes |
| **Cricket** | Fermer 20 → 15 et le bull, trois marques par numéro. | Standard, Cut-throat, Fermeture seule |
| **Around the Clock** | Faire 1, 2, 3… jusqu'au 20 puis le bull. | Progression simple ou rapide, doubles uniquement, bull final |
| **Shanghai** | Un numéro par tour ; simple + double + triple dans le même tour = victoire immédiate. | Nombre de tours, premier numéro, Shanghai gagnant |
| **Killer** | Chacun son numéro : on gagne des vies, puis on retire celles des autres. | Vies pour devenir killer, doubles uniquement, pénalité sur son propre numéro |

Le 501 affiche la **suggestion de sortie** (« T20 → T20 → D19 ») et met les
secteurs concernés en évidence sur le pavé. Le Cricket, l'Around the Clock,
le Shanghai et le Killer éclairent eux aussi les cibles utiles du moment.

## Piloter la borne

Un vieux portable a rarement un écran tactile. Quatre façons de saisir, toutes
utilisables en même temps :

* **écran tactile** (si vous en ajoutez un) — le pavé est dimensionné pour ça ;
* **souris ou pavé tactile** du portable ;
* **clavier ou pavé numérique déporté** — voir les raccourcis ci-dessous ;
* **téléphone ou tablette** sur le même wifi, à l'adresse `http://<ip-du-pc>:8080`.
  Tous les écrans branchés sur la partie restent synchronisés.

### Raccourcis clavier

| Touche | Effet |
| --- | --- |
| `1` … `20` | Lance la fléchette sur ce numéro (tapez `2` puis `0` pour 20) |
| `s` / `d` / `t` | Simple / Double / Triple pour la fléchette suivante |
| `b` | Bull (25, ou 50 si `d` est actif) |
| `m` | Fléchette manquée |
| `Retour arrière` | Annule la dernière fléchette |
| `Espace` / `Entrée` | Passe l'écran de changement de joueur |

Un pavé numérique sans fil accroché au mur près de la cible transforme
n'importe quel portable en borne utilisable à bout de bras.

## Ce que la borne retient

Chaque fléchette est enregistrée au fil de l'eau dans une base SQLite
(`data/raspydarts.sqlite3`). En pratique :

* une coupure de courant ne coûte rien — la partie **reprend où elle en était** ;
* l'annulation rejoue l'historique depuis le début, donc elle est toujours exacte ;
* les fiches joueurs cumulent parties, victoires, meilleure moyenne, meilleur
  finish, meilleure manche, MPR au Cricket et nombre de 180.

## Organisation du code

```
app/
  throws.py       fléchette : secteur, multiplicateur, valeur
  checkout.py     recherche du chemin de sortie le plus court
  games/
    base.py       socle commun : tours, rotation, annulation, état
    x01.py  cricket.py  around_the_clock.py  shanghai.py  killer.py
  db.py           SQLite : joueurs, parties, statistiques
  session.py      la partie en cours + sauvegarde continue
  server.py       API JSON et service des fichiers de l'interface
web/              interface tactile (HTML, CSS, modules ES — aucun build)
scripts/          lancement Linux et Windows, unité systemd
tests/            règles des jeux, API, parcours navigateur
```

Le cœur du moteur est un **réducteur pur** : l'état complet se recalcule en
rejouant la liste des fléchettes. C'est ce qui rend l'annulation et la reprise
après coupure fiables sans code particulier.

## API

| Méthode | Route | Rôle |
| --- | --- | --- |
| `GET` | `/api/bootstrap` | Jeux, joueurs, partie en cours, dernières parties |
| `GET` `POST` `DELETE` | `/api/players` | Gestion des joueurs |
| `GET` | `/api/players/<id>/stats` | Fiche statistique d'un joueur |
| `GET` `POST` `DELETE` | `/api/match` | Lire, démarrer, abandonner la partie |
| `POST` | `/api/match/throw` | `{"multiplier": 3, "sector": 20}` |
| `POST` | `/api/match/undo` | Annule la dernière fléchette |
| `GET` | `/api/matches` | Historique des parties terminées |

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q            # règles + API
playwright install chromium          # une fois, pour les tests d'interface
python -m pytest tests/test_interface.py -q
```

Les tests d'interface pilotent un vrai Chromium : ils déroulent une partie
complète, vérifient l'annulation, la reprise après rechargement et la
synchronisation entre deux écrans. Ils sont ignorés si Playwright est absent.
