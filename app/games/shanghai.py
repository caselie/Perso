"""Shanghai — un numéro par tour, le plus gros total gagne."""

from __future__ import annotations

from ..throws import Throw
from .base import Game, Outcome


class Shanghai(Game):
    slug = "shanghai"
    label = "Shanghai"
    description = "Tour 1 : le 1, tour 2 : le 2… Simple + double + triple dans le même tour = victoire immédiate."
    min_players = 1
    max_players = 8
    OPTIONS = [
        {"key": "rounds", "label": "Nombre de tours", "type": "int", "min": 2, "max": 20, "default": 7},
        {"key": "start", "label": "Premier numéro", "type": "int", "min": 1, "max": 20, "default": 1},
        {"key": "shanghai_wins", "label": "Shanghai = victoire immédiate", "type": "bool", "default": True},
    ]

    def setup(self) -> None:
        self.scores = [0] * len(self.players)
        self._turn_multipliers: set[int] = set()

    @property
    def target(self) -> int:
        number = self.options["start"] + self.round - 1
        return (number - 1) % 20 + 1

    def on_turn_start(self) -> None:
        self._turn_multipliers = set()
        if self.round > self.options["rounds"] and not self.finished:
            best = max(range(len(self.players)), key=lambda i: self.scores[i])
            self.win(best)

    def on_throw(self, throw: Throw) -> Outcome | None:
        if throw.sector != self.target:
            return None
        p = self.current
        self.scores[p] += throw.value
        self._turn_multipliers.add(throw.multiplier)

        if self.options["shanghai_wins"] and {1, 2, 3} <= self._turn_multipliers:
            self.win(p)
            return Outcome(end_turn=True, note="SHANGHAI !")
        return None

    def prompt(self) -> str:
        last = self.options["rounds"]
        return f"Tour {min(self.round, last)}/{last} — visez le {self.target}"

    def highlights(self) -> list[int]:
        return [self.target]

    def scoreboard(self) -> list[dict]:
        return [
            {"score": self.scores[i], "detail": f"{self.scores[i]} pts"}
            for i in range(len(self.players))
        ]

    def stats(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            darts = self.darts_by_player[i]
            rows.append(
                {
                    "darts": darts,
                    "points": self.scores[i],
                    "average3": round(self.scores[i] / darts * 3, 2) if darts else 0.0,
                }
            )
        return rows
