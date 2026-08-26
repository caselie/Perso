"""Cricket — fermer les 20 à 15 et le bull, avec ou sans points."""

from __future__ import annotations

from ..throws import Throw
from .base import Game, Outcome

TARGETS: tuple[int, ...] = (20, 19, 18, 17, 16, 15, 25)
MARKS_TO_CLOSE = 3


class Cricket(Game):
    slug = "cricket"
    label = "Cricket"
    description = "Fermez 20, 19, 18, 17, 16, 15 et le bull. Trois marques par numéro."
    min_players = 1
    max_players = 6
    OPTIONS = [
        {
            "key": "variant",
            "label": "Variante",
            "type": "choice",
            "choices": ["standard", "cutthroat", "fermeture"],
            "labels": {
                "standard": "Standard (points pour soi)",
                "cutthroat": "Cut-throat (points aux autres)",
                "fermeture": "Fermeture seule (sans points)",
            },
            "default": "standard",
        },
    ]

    # ---------------------------------------------------------------- état

    def setup(self) -> None:
        n = len(self.players)
        self.marks = [{t: 0 for t in TARGETS} for _ in range(n)]
        self.scores = [0] * n
        self.hit_marks = [0] * n  # marques utiles, pour la stat MPR

    @property
    def variant(self) -> str:
        return self.options["variant"]

    def closed(self, player: int, target: int) -> bool:
        return self.marks[player][target] >= MARKS_TO_CLOSE

    def has_closed_all(self, player: int) -> bool:
        return all(self.closed(player, t) for t in TARGETS)

    def is_dead(self, target: int) -> bool:
        return all(self.closed(p, target) for p in range(len(self.players)))

    # --------------------------------------------------------------- règles

    def on_throw(self, throw: Throw) -> Outcome | None:
        target = throw.sector
        if target not in TARGETS:
            return None

        p = self.current
        marks = min(throw.multiplier, MARKS_TO_CLOSE - self.marks[p][target])
        overflow = throw.multiplier - marks
        self.marks[p][target] += marks
        self.hit_marks[p] += marks

        if overflow and self.variant != "fermeture":
            self.hit_marks[p] += overflow
            self._score(p, target, overflow)

        return self._check_end(p)

    def _score(self, player: int, target: int, marks: int) -> None:
        open_rivals = [
            q
            for q in range(len(self.players))
            if q != player and not self.closed(q, target)
        ]
        if not open_rivals:
            return  # numéro mort : plus aucun point possible dessus
        points = marks * target
        if self.variant == "cutthroat":
            for q in open_rivals:
                self.scores[q] += points
        else:
            self.scores[player] += points

    def _check_end(self, player: int) -> Outcome | None:
        if self.has_closed_all(player) and self._is_ahead(player):
            self.win(player)
            return Outcome(end_turn=True, note="GAGNÉ")
        if all(self.is_dead(t) for t in TARGETS):
            self.win(self._best_player())
            return Outcome(end_turn=True, note="TOUT FERMÉ")
        return None

    def _is_ahead(self, player: int) -> bool:
        rivals = [self.scores[q] for q in range(len(self.players)) if q != player]
        if not rivals or self.variant == "fermeture":
            return True
        if self.variant == "cutthroat":
            return self.scores[player] <= min(rivals)
        return self.scores[player] >= max(rivals)

    def _best_player(self) -> int:
        order = range(len(self.players))
        if self.variant == "cutthroat":
            return min(order, key=lambda i: self.scores[i])
        if self.variant == "fermeture":
            return max(order, key=lambda i: sum(self.marks[i].values()))
        return max(order, key=lambda i: self.scores[i])

    # ------------------------------------------------------------ affichage

    def prompt(self) -> str:
        p = self.current
        restants = [
            str(t) if t != 25 else "bull"
            for t in TARGETS
            if not self.closed(p, t)
        ]
        if restants:
            return "À fermer : " + ", ".join(restants)
        vivants = [
            str(t) if t != 25 else "bull" for t in TARGETS if not self.is_dead(t)
        ]
        if vivants and self.variant != "fermeture":
            return "Tout fermé — marquez sur : " + ", ".join(vivants)
        return "Tout fermé"

    def highlights(self) -> list[int]:
        """Numéros encore utiles : non fermés par le joueur, ou pas encore morts."""
        p = self.current
        return [t for t in TARGETS if not self.closed(p, t) or not self.is_dead(t)]

    def scoreboard(self) -> list[dict]:
        return [
            {
                "score": self.scores[i],
                "marks": [
                    {"target": t, "marks": self.marks[i][t], "dead": self.is_dead(t)}
                    for t in TARGETS
                ],
                "closed_all": self.has_closed_all(i),
                "detail": f"{self.scores[i]} pts",
            }
            for i in range(len(self.players))
        ]

    def stats(self) -> list[dict]:
        rows = []
        for i in range(len(self.players)):
            darts = self.darts_by_player[i]
            marks = self.hit_marks[i]
            rows.append(
                {
                    "darts": darts,
                    "points": self.scores[i],
                    "marks": marks,
                    # MPR : marques par volée de 3 fléchettes
                    "mpr": round(marks / darts * 3, 2) if darts else 0.0,
                    "average3": round(self.points_by_player[i] / darts * 3, 2) if darts else 0.0,
                }
            )
        return rows
