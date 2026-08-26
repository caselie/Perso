"""Représentation d'une fléchette et de son score.

Une fléchette est décrite par un secteur et un multiplicateur :

* secteur ``0``       -> hors cible (multiplicateur toujours 1, valeur 0)
* secteur ``1..20``   -> multiplicateur 1 (simple), 2 (double) ou 3 (triple)
* secteur ``25``      -> multiplicateur 1 (bull, 25 pts) ou 2 (bull's eye, 50 pts)
"""

from __future__ import annotations

from dataclasses import dataclass

MISS = 0
BULL = 25
NUMBERS = tuple(range(1, 21))
SECTORS = (MISS,) + NUMBERS + (BULL,)


class InvalidThrow(ValueError):
    """Combinaison secteur / multiplicateur impossible sur une cible."""


@dataclass(frozen=True)
class Throw:
    multiplier: int
    sector: int

    def __post_init__(self) -> None:
        if self.sector not in SECTORS:
            raise InvalidThrow(f"secteur inconnu : {self.sector}")
        if self.sector == MISS and self.multiplier != 1:
            raise InvalidThrow("une fléchette hors cible n'a pas de multiplicateur")
        if self.sector == BULL and self.multiplier not in (1, 2):
            raise InvalidThrow("le bull n'accepte que le simple (25) ou le double (50)")
        if self.sector in NUMBERS and self.multiplier not in (1, 2, 3):
            raise InvalidThrow(f"multiplicateur invalide : {self.multiplier}")

    @property
    def value(self) -> int:
        """Points marqués par la fléchette."""
        return self.sector * self.multiplier

    @property
    def is_miss(self) -> bool:
        return self.sector == MISS

    @property
    def is_double(self) -> bool:
        """Vrai pour un double, bull's eye compris (finish au double autorisé)."""
        return self.multiplier == 2

    @property
    def is_triple(self) -> bool:
        return self.multiplier == 3 and self.sector in NUMBERS

    @property
    def label(self) -> str:
        if self.is_miss:
            return "—"
        if self.sector == BULL:
            return "50" if self.multiplier == 2 else "25"
        return f"{'SDT'[self.multiplier - 1]}{self.sector}"

    def to_dict(self) -> dict:
        return {
            "multiplier": self.multiplier,
            "sector": self.sector,
            "value": self.value,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Throw":
        return cls(int(data["multiplier"]), int(data["sector"]))


def miss() -> Throw:
    return Throw(1, MISS)


def single(sector: int) -> Throw:
    return Throw(1, sector)


def double(sector: int) -> Throw:
    return Throw(2, sector)


def triple(sector: int) -> Throw:
    return Throw(3, sector)
