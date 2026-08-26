"""Killer — chacun son numéro, on gagne des vies puis on élimine les autres."""

from __future__ import annotations

import random

from ..throws import Throw
from .base import Game, Outcome


class Killer(Game):
    slug = "killer"
    label = "Killer"
    description = (
        "Chaque joueur reçoit un numéro. Touchez le vôtre pour gagner des vies ; "
        "une fois « killer », touchez celui des autres pour leur en retirer."
    )
    min_players = 2
    max_players = 8
    elimination_wins = True
    OPTIONS = [
        {"key": "lives", "label": "Vies pour devenir killer", "type": "int", "min": 1, "max": 5, "default": 3},
        {
            "key": "double_only",
            "label": "Doubles uniquement",
            "type": "bool",
            "default": False,
        },
        {
            "key": "self_penalty",
            "label": "Un killer qui touche son propre numéro perd une vie",
            "type": "bool",
            "default": True,
        },
        # Renseignée par le serveur à la création : rend l'attribution des
        # numéros reproductible, donc l'annulation fiable.
        {"key": "seed", "label": "", "type": "int", "min": 0, "max": 10**9, "default": 0, "hidden": True},
    ]

    def setup(self) -> None:
        n = len(self.players)
        pool = list(range(1, 21))
        random.Random(self.options["seed"]).shuffle(pool)
        self.numbers = pool[:n]
        self.lives = [0] * n
        self.armed = [False] * n  # a déjà gagné au moins une vie
        self.kills = [0] * n

    @property
    def max_lives(self) -> int:
        return self.options["lives"]

    def is_killer(self, player: int) -> bool:
        return self.lives[player] >= self.max_lives

    def owner_of(self, sector: int) -> int | None:
        for i, number in enumerate(self.numbers):
            if number == sector and i not in self.eliminated:
                return i
        return None

    def on_throw(self, throw: Throw) -> Outcome | None:
        if self.options["double_only"] and not throw.is_double:
            return None
        target = self.owner_of(throw.sector)
        if target is None:
            return None

        p = self.current
        marks = throw.multiplier

        if target == p:
            if self.is_killer(p) and self.options["self_penalty"]:
                self._remove_lives(p, marks, by=p)
            else:
                self.lives[p] = min(self.max_lives, self.lives[p] + marks)
                self.armed[p] = True
            return None

        if not self.is_killer(p):
            return None  # pas encore killer : les autres ne risquent rien
        self._remove_lives(target, marks, by=p)
        return None

    def _remove_lives(self, victim: int, marks: int, by: int) -> None:
        self.lives[victim] = max(0, self.lives[victim] - marks)
        if by != victim:
            self.kills[by] += marks
        if self.armed[victim] and self.lives[victim] == 0:
            self.eliminate(victim)

    def prompt(self) -> str:
        p = self.current
        mien = self.numbers[p]
        if not self.is_killer(p):
            manque = self.max_lives - self.lives[p]
            return f"Votre numéro : {mien} — encore {manque} vie(s) pour devenir killer"
        cibles = ", ".join(
            str(self.numbers[q]) for q in self.active_players() if q != p
        )
        return f"KILLER ! Visez : {cibles}" if cibles else "KILLER !"

    def highlights(self) -> list[int]:
        p = self.current
        if not self.is_killer(p):
            return [self.numbers[p]]
        return [self.numbers[q] for q in self.active_players()]

    def scoreboard(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            rows.append(
                {
                    "score": self.lives[i],
                    "number": self.numbers[i],
                    "killer": self.is_killer(i),
                    "lives": self.lives[i],
                    "max_lives": self.max_lives,
                    "detail": f"n°{self.numbers[i]} — {self.lives[i]} vie(s)",
                }
            )
        return rows

    def stats(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            darts = self.darts_by_player[i]
            rows.append(
                {
                    "darts": darts,
                    "points": self.kills[i],
                    "kills": self.kills[i],
                    "number": self.numbers[i],
                    "average3": round(self.points_by_player[i] / darts * 3, 2) if darts else 0.0,
                }
            )
        return rows
