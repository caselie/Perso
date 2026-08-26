"""Catalogue des jeux disponibles sur la borne."""

from .around_the_clock import AroundTheClock
from .base import Game, GameError, Outcome
from .cricket import Cricket
from .killer import Killer
from .shanghai import Shanghai
from .x01 import X01

GAMES: dict[str, type[Game]] = {
    cls.slug: cls for cls in (X01, Cricket, AroundTheClock, Shanghai, Killer)
}

__all__ = ["GAMES", "Game", "GameError", "Outcome", "catalogue", "build"]


def catalogue() -> list[dict]:
    return [cls.describe() for cls in GAMES.values()]


def build(slug: str, players: list[str], options: dict | None = None) -> Game:
    if slug not in GAMES:
        raise GameError(f"jeu inconnu : {slug}")
    return GAMES[slug](players, options)
