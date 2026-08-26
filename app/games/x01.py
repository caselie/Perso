"""501 / 301 / 701 — décompte jusqu'à zéro."""

from __future__ import annotations

from ..checkout import checkout_route
from ..throws import Throw
from .base import Game, Outcome


class X01(Game):
    slug = "x01"
    label = "501 / 301"
    description = "Décompte jusqu'à zéro pile. Sortie au double, bust, manches."
    min_players = 1
    max_players = 8
    OPTIONS = [
        {
            "key": "start",
            "label": "Score de départ",
            "type": "int",
            "min": 2,
            "max": 1001,
            "default": 501,
            "presets": [101, 301, 501, 701, 1001],
        },
        {"key": "double_out", "label": "Sortie au double", "type": "bool", "default": True},
        {"key": "double_in", "label": "Entrée au double", "type": "bool", "default": False},
        {
            "key": "legs",
            "label": "Manches gagnantes",
            "type": "int",
            "min": 1,
            "max": 9,
            "default": 1,
        },
    ]

    # ---------------------------------------------------------------- état

    def setup(self) -> None:
        n = len(self.players)
        start = self.options["start"]
        self.scores = [start] * n
        self.opened = [not self.options["double_in"]] * n
        self.legs_won = [0] * n
        self.scored = [0] * n  # points réellement décomptés (hors bust)
        self.leg_darts = [0] * n
        self.best_leg = [None] * n  # meilleure manche, en fléchettes
        self.tons = [0] * n  # volées à 100 et plus
        self.max_180 = [0] * n
        self.best_checkout = [0] * n
        self.checkout_tries = [0] * n
        self.checkout_hits = [0] * n
        self.leg_starter = 0

    def on_turn_start(self) -> None:
        p = self.current
        self._snapshot = (self.scores[p], self.opened[p], self.scored[p])
        self._busted = False

    def on_turn_end(self) -> None:
        if self._busted:
            return
        p = self.last_turn.player if self.last_turn else self.current
        points = self.scored[p] - self._snapshot[2]
        if points >= 100:
            self.tons[p] += 1
        if points == 180:
            self.max_180[p] += 1

    # --------------------------------------------------------------- règles

    def on_throw(self, throw: Throw) -> Outcome | None:
        p = self.current
        self.leg_darts[p] += 1

        if not self.opened[p]:
            if not throw.is_double:
                return None  # tant que le double d'entrée n'est pas touché
            self.opened[p] = True

        double_out = self.options["double_out"]
        before = self.scores[p]
        remaining = before - throw.value
        # « Sur un double » : le score restant peut se conclure avec cette
        # fléchette. Chaque fléchette lancée dans cette position compte comme
        # une tentative de sortie, qu'elle touche ou non.
        on_a_double = checkout_route(before, 1, double_out) is not None
        if on_a_double:
            self.checkout_tries[p] += 1

        if remaining == 0 and (throw.is_double or not double_out):
            self.scored[p] += throw.value
            self.scores[p] = 0
            self._register_checkout(p, self._snapshot[0])
            return self._win_leg(p)

        if remaining < 0 or remaining == 0 or (remaining == 1 and double_out):
            return self._bust(p)

        self.scored[p] += throw.value
        self.scores[p] = remaining
        return None

    def _bust(self, player: int) -> Outcome:
        score, opened, scored = self._snapshot
        self.scores[player] = score
        self.opened[player] = opened
        self.scored[player] = scored
        self._busted = True
        return Outcome(end_turn=True, note="BUST")

    def _register_checkout(self, player: int, visit_start: int) -> None:
        """Enregistre une sortie réussie ; le « best checkout » est le total
        effacé sur l'ensemble de la volée, comme au comptage officiel."""
        self.checkout_hits[player] += 1
        self.best_checkout[player] = max(self.best_checkout[player], visit_start)

    def _win_leg(self, player: int) -> Outcome:
        darts = self.leg_darts[player]
        current_best = self.best_leg[player]
        if current_best is None or darts < current_best:
            self.best_leg[player] = darts
        self.legs_won[player] += 1

        if self.legs_won[player] >= self.options["legs"]:
            self.win(player)
            return Outcome(end_turn=True, note="GAGNÉ")

        start = self.options["start"]
        self.scores = [start] * len(self.players)
        self.opened = [not self.options["double_in"]] * len(self.players)
        self.leg_darts = [0] * len(self.players)
        self.leg_starter = (self.leg_starter + 1) % len(self.players)
        return Outcome(
            end_turn=True, next_player=self.leg_starter, reset_round=True, note="MANCHE"
        )

    # ------------------------------------------------------------ affichage

    def prompt(self) -> str:
        p = self.current
        if not self.opened[p]:
            return "Entrée au double : touchez un double pour démarrer"
        left = self.darts_per_turn - self.darts
        route = checkout_route(self.scores[p], left, self.options["double_out"])
        if route:
            return "Sortie : " + " → ".join(t.label for t in route)
        return ""

    def highlights(self) -> list[int]:
        left = self.darts_per_turn - self.darts
        route = checkout_route(self.scores[self.current], left, self.options["double_out"])
        return sorted({t.sector for t in route}) if route else []

    def scoreboard(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            route = checkout_route(self.scores[i], 3, self.options["double_out"])
            rows.append(
                {
                    "score": self.scores[i],
                    "legs": self.legs_won[i],
                    "opened": self.opened[i],
                    "checkout": " ".join(t.label for t in route) if route else "",
                    "detail": f"{self.scores[i]}",
                }
            )
        return rows

    def stats(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            darts = self.darts_by_player[i]
            scored = self.scored[i]
            tries, hits = self.checkout_tries[i], self.checkout_hits[i]
            rows.append(
                {
                    "darts": darts,
                    "points": scored,
                    "average3": round(scored / darts * 3, 2) if darts else 0.0,
                    "best_leg": self.best_leg[i],
                    "tons": self.tons[i],
                    "count_180": self.max_180[i],
                    "best_checkout": self.best_checkout[i],
                    "checkout_pct": round(hits / tries * 100, 1) if tries else 0.0,
                }
            )
        return rows
