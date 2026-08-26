"""Around the Clock — faire 1 à 20 puis le bull, dans l'ordre."""

from __future__ import annotations

from ..throws import Throw
from .base import Game, Outcome


class AroundTheClock(Game):
    slug = "atc"
    label = "Around the Clock"
    description = "Touchez 1, puis 2, puis 3… jusqu'au 20 et au bull. Idéal à l'échauffement."
    min_players = 1
    max_players = 8
    OPTIONS = [
        {
            "key": "mode",
            "label": "Progression",
            "type": "choice",
            "choices": ["simple", "rapide"],
            "labels": {
                "simple": "Simple (un numéro à la fois)",
                "rapide": "Rapide (le double avance de 2, le triple de 3)",
            },
            "default": "simple",
        },
        {"key": "double_only", "label": "Doubles uniquement", "type": "bool", "default": False},
        {"key": "include_bull", "label": "Finir sur le bull", "type": "bool", "default": True},
    ]

    def setup(self) -> None:
        self.targets = list(range(1, 21))
        if self.options["include_bull"]:
            self.targets.append(25)
        self.progress = [0] * len(self.players)
        self.hits = [0] * len(self.players)

    def target_for(self, player: int) -> int | None:
        index = self.progress[player]
        return self.targets[index] if index < len(self.targets) else None

    def on_throw(self, throw: Throw) -> Outcome | None:
        p = self.current
        target = self.target_for(p)
        if target is None or throw.sector != target:
            return None
        if self.options["double_only"] and not throw.is_double:
            return None

        step = throw.multiplier if self.options["mode"] == "rapide" else 1
        self.progress[p] = min(self.progress[p] + step, len(self.targets))
        self.hits[p] += 1

        if self.progress[p] >= len(self.targets):
            self.win(p)
            return Outcome(end_turn=True, note="GAGNÉ")
        return None

    def prompt(self) -> str:
        target = self.target_for(self.current)
        if target is None:
            return "Terminé"
        nom = "bull" if target == 25 else str(target)
        if self.options["double_only"]:
            return f"Visez le double {nom}"
        return f"Visez le {nom}"

    def highlights(self) -> list[int]:
        target = self.target_for(self.current)
        return [target] if target else []

    def scoreboard(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            target = self.target_for(i)
            rows.append(
                {
                    "score": self.progress[i],
                    "target": target,
                    "total": len(self.targets),
                    "detail": ("fini" if target is None else f"cible {target if target != 25 else 'bull'}"),
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
                    "points": self.progress[i],
                    "hits": self.hits[i],
                    "hit_pct": round(self.hits[i] / darts * 100, 1) if darts else 0.0,
                    "average3": round(self.points_by_player[i] / darts * 3, 2) if darts else 0.0,
                }
            )
        return rows
