"""Partie courante de la borne.

Une borne, une cible, une partie à la fois : le serveur garde un seul match
en mémoire et le recopie dans la base après chaque fléchette, pour qu'une
coupure de courant ne coûte rien.
"""

from __future__ import annotations

import random
import threading

from .db import Database
from .games import GAMES, Game, GameError, build
from .throws import Throw


class Session:
    def __init__(self, db: Database):
        self.db = db
        self.lock = threading.RLock()
        self.game: Game | None = None
        self.match_id: int | None = None
        self.seats: list[dict] = []
        self._saved = False
        # Compteur croissant à chaque changement : les écrans branchés sur la
        # même partie (grand écran + téléphone) ignorent les réponses périmées.
        self.revision = 0
        self.resume()

    # ------------------------------------------------------------ cycle de vie

    def resume(self) -> None:
        """Recharge la partie interrompue au démarrage, si elle existe."""
        record = self.db.open_match()
        if not record or record["game"] not in GAMES:
            return
        try:
            game = build(
                record["game"], [seat["name"] for seat in record["seats"]], record["options"]
            )
            for dart in record["history"]:
                game.throw(Throw.from_dict(dart))
        except (GameError, ValueError, KeyError):
            self.db.abandon_match(record["id"])
            return
        self.game = game
        self.match_id = record["id"]
        self.seats = record["seats"]
        self.revision += 1

    def start(self, slug: str, seats: list[dict], options: dict | None = None) -> dict:
        with self.lock:
            self.abandon()
            options = dict(options or {})
            if slug == "killer" and not options.get("seed"):
                options["seed"] = random.randrange(1, 10**9)
            game = build(slug, [seat["name"] for seat in seats], options)
            self.game = game
            self.seats = seats
            self.match_id = self.db.create_match(slug, game.options, seats)
            self._saved = False
            self.revision += 1
            return self.state()

    def abandon(self) -> None:
        with self.lock:
            if self.match_id is not None and not self._saved:
                self.db.abandon_match(self.match_id)
            self.game = None
            self.match_id = None
            self.seats = []
            self._saved = False
            self.revision += 1

    # ---------------------------------------------------------------- actions

    def require(self) -> Game:
        if self.game is None:
            raise GameError("aucune partie en cours")
        return self.game

    def throw(self, multiplier: int, sector: int) -> dict:
        with self.lock:
            game = self.require()
            game.throw(Throw(multiplier, sector))
            self.revision += 1
            self._persist()
            return self.state()

    def undo(self) -> dict:
        with self.lock:
            game = self.require()
            if self._saved:
                raise GameError("partie terminée et enregistrée : impossible d'annuler")
            game.undo()
            self.revision += 1
            self._persist()
            return self.state()

    def _persist(self) -> None:
        game, match_id = self.game, self.match_id
        if game is None or match_id is None:
            return
        self.db.save_history(match_id, [dart.to_dict() for dart in game.history])
        if game.finished and not self._saved:
            self.db.finish_match(match_id, game.winner, self.seats, game.stats())
            self._saved = True

    # ------------------------------------------------------------------- état

    def state(self) -> dict | None:
        game = self.game
        if game is None:
            return None
        state = game.state()
        state["match_id"] = self.match_id
        state["seats"] = self.seats
        state["saved"] = self._saved
        state["revision"] = self.revision
        return state
