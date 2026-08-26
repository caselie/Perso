"""Socle commun à tous les jeux.

Chaque partie est un *réducteur pur* : l'état complet se recalcule en rejouant
l'historique des fléchettes depuis le début. Annuler une fléchette revient donc
à retirer la dernière entrée de l'historique puis à tout rejouer — pas d'état
caché, pas d'annulation à moitié faite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..throws import Throw


class GameError(RuntimeError):
    """Action impossible dans l'état courant de la partie."""


@dataclass
class Outcome:
    """Ce que les règles du jeu décident après une fléchette."""

    end_turn: bool = False
    next_player: int | None = None  # impose le prochain joueur (nouvelle manche)
    reset_round: bool = False
    note: str = ""  # "BUST", "SHANGHAI", "LEG"… affiché par l'interface


@dataclass
class TurnSummary:
    player: int
    throws: list[dict]
    points: int
    note: str
    round: int


class Game:
    """Classe de base. Les sous-classes implémentent les règles."""

    slug: str = ""
    label: str = ""
    description: str = ""
    min_players: int = 1
    max_players: int = 8
    darts_per_turn: int = 3
    #: le jeu se termine dès qu'il ne reste qu'un joueur non éliminé
    elimination_wins: bool = False
    OPTIONS: list[dict] = []

    # ------------------------------------------------------------------ setup

    def __init__(self, players: list[str], options: dict | None = None):
        if not self.min_players <= len(players) <= self.max_players:
            raise GameError(
                f"{self.label} se joue de {self.min_players} à {self.max_players} joueurs"
            )
        self.players = list(players)
        self.options = self.normalise_options(options or {})
        self.history: list[Throw] = []
        self._rebuild()

    @classmethod
    def normalise_options(cls, raw: dict) -> dict:
        """Valide et complète les options fournies par l'interface."""
        clean: dict[str, Any] = {}
        for spec in cls.OPTIONS:
            key = spec["key"]
            value = raw.get(key, spec["default"])
            kind = spec["type"]
            if kind == "bool":
                value = bool(value)
            elif kind == "int":
                value = int(value)
                value = max(spec.get("min", value), min(spec.get("max", value), value))
            elif kind == "choice":
                choices = spec["choices"]
                if value not in choices:
                    value = spec["default"]
            clean[key] = value
        return clean

    @classmethod
    def describe(cls) -> dict:
        return {
            "slug": cls.slug,
            "label": cls.label,
            "description": cls.description,
            "min_players": cls.min_players,
            "max_players": cls.max_players,
            "options": cls.OPTIONS,
        }

    # ------------------------------------------------------------- hooks jeu

    def setup(self) -> None:
        """Initialise l'état propre au jeu (appelé à chaque recalcul)."""

    def on_turn_start(self) -> None:
        """Début de volée. Peut terminer la partie (limite de tours atteinte)."""

    def on_turn_end(self) -> None:
        """Fin de volée, avant de passer au joueur suivant."""

    def on_throw(self, throw: Throw) -> Outcome | None:
        """Applique les règles à une fléchette."""
        raise NotImplementedError

    def scoreboard(self) -> list[dict]:
        """Ligne de tableau de score par joueur, pour l'interface."""
        raise NotImplementedError

    def prompt(self) -> str:
        """Consigne affichée au joueur courant (cible à viser, finish…)."""
        return ""

    def highlights(self) -> list[int]:
        """Secteurs à mettre en avant sur le pavé de saisie."""
        return []

    # ------------------------------------------------------------ mécanique

    def throw(self, dart: Throw) -> None:
        if self.finished:
            raise GameError("la partie est terminée")
        self.history.append(dart)
        self._consume(dart)

    def undo(self) -> bool:
        if not self.history:
            return False
        self.history.pop()
        self._rebuild()
        return True

    def _rebuild(self) -> None:
        self.current = 0
        self.darts = 0
        self.round = 1
        self.finished = False
        self.winner: int | None = None
        self.ranking: list[int] = []
        self.eliminated: set[int] = set()
        self.turn_throws: list[Throw] = []
        self.turn_note = ""
        self.last_turn: TurnSummary | None = None
        self.darts_by_player = [0] * len(self.players)
        self.points_by_player = [0] * len(self.players)
        self.setup()
        self.on_turn_start()
        for dart in list(self.history):
            self._consume(dart)

    def _consume(self, dart: Throw) -> None:
        outcome = self.on_throw(dart) or Outcome()
        self.turn_throws.append(dart)
        self.darts += 1
        self.darts_by_player[self.current] += 1
        self.points_by_player[self.current] += dart.value
        if outcome.note:
            self.turn_note = outcome.note

        if self.elimination_wins and not self.finished:
            active = self.active_players()
            if len(active) == 1:
                self.win(active[0])

        if self.finished:
            self._close_turn()
            return
        if outcome.end_turn or self.darts >= self.darts_per_turn:
            self._advance(outcome.next_player, outcome.reset_round)

    def _close_turn(self) -> None:
        self.last_turn = TurnSummary(
            player=self.current,
            throws=[t.to_dict() for t in self.turn_throws],
            points=sum(t.value for t in self.turn_throws),
            note=self.turn_note,
            round=self.round,
        )

    def _advance(self, forced: int | None, reset_round: bool) -> None:
        self._close_turn()
        self.on_turn_end()
        nxt = forced if forced is not None else self.next_active(self.current)
        if reset_round:
            self.round = 1
        elif nxt <= self.current:
            self.round += 1
        self.current = nxt
        self.darts = 0
        self.turn_throws = []
        self.turn_note = ""
        self.on_turn_start()

    # -------------------------------------------------------------- joueurs

    def active_players(self) -> list[int]:
        return [i for i in range(len(self.players)) if i not in self.eliminated]

    def next_active(self, start: int) -> int:
        n = len(self.players)
        for step in range(1, n + 1):
            candidate = (start + step) % n
            if candidate not in self.eliminated:
                return candidate
        return start

    def eliminate(self, index: int) -> None:
        if index not in self.eliminated:
            self.eliminated.add(index)
            self.ranking.append(index)

    def win(self, index: int) -> None:
        self.finished = True
        self.winner = index
        if index not in self.ranking:
            self.ranking.append(index)

    # ------------------------------------------------------------------ état

    def stats(self) -> list[dict]:
        rows = []
        for i, _ in enumerate(self.players):
            darts = self.darts_by_player[i]
            points = self.points_by_player[i]
            rows.append(
                {
                    "darts": darts,
                    "points": points,
                    "average3": round(points / darts * 3, 2) if darts else 0.0,
                }
            )
        return rows

    def state(self) -> dict:
        stats = self.stats()
        board = self.scoreboard()
        for i, row in enumerate(board):
            row.setdefault("name", self.players[i])
            row["index"] = i
            row["active"] = i == self.current
            row["eliminated"] = i in self.eliminated
            row["stats"] = stats[i]
        return {
            "game": self.slug,
            "label": self.label,
            "options": self.options,
            "players": self.players,
            "current": self.current,
            "round": self.round,
            "darts_left": self.darts_per_turn - self.darts,
            "turn_throws": [t.to_dict() for t in self.turn_throws],
            "turn_note": self.turn_note,
            "prompt": self.prompt(),
            "highlights": self.highlights(),
            "scoreboard": board,
            "finished": self.finished,
            "winner": self.winner,
            "ranking": self.ranking,
            "history_length": len(self.history),
            "last_turn": (
                {
                    "player": self.last_turn.player,
                    "name": self.players[self.last_turn.player],
                    "throws": self.last_turn.throws,
                    "points": self.last_turn.points,
                    "note": self.last_turn.note,
                    "round": self.last_turn.round,
                }
                if self.last_turn
                else None
            ),
        }
