"""Suggestion de finish (checkout) pour les jeux x01.

Calcule à la volée un chemin de sortie plausible plutôt que d'embarquer la
table des 170 finishes : le résultat est mis en cache, le coût est nul en
pratique.
"""

from __future__ import annotations

from functools import lru_cache

from .throws import Throw, double, single, triple

#: ordre de préférence des fléchettes de préparation (le triple 20 d'abord,
#: puis les gros triples, puis les simples qui laissent un double confortable)
_SETUP: tuple[Throw, ...] = (
    tuple(triple(n) for n in (20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1))
    + (double(25), single(25))
    + tuple(single(n) for n in (20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1))
    + tuple(double(n) for n in (20, 18, 16, 12, 10, 8, 6, 4, 2, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1))
)

#: doubles de sortie, du plus confortable au moins confortable
_FINISH: tuple[Throw, ...] = tuple(
    double(n) for n in (20, 16, 18, 12, 10, 8, 14, 4, 6, 2, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1)
) + (double(25),)


@lru_cache(maxsize=4096)
def checkout_route(score: int, darts: int, double_out: bool = True) -> tuple[Throw, ...] | None:
    """Chemin de sortie le plus court en ``darts`` fléchettes au plus.

    La recherche essaie d'abord une fléchette, puis deux, puis trois : le joueur
    voit toujours la sortie la plus directe.
    """
    if score <= 0 or darts <= 0 or score > 60 * darts:
        return None
    finishes = _FINISH if double_out else _FINISH + _SETUP
    for depth in range(1, darts + 1):
        route = _search(score, depth, finishes)
        if route:
            return route
    return None


def _search(score: int, depth: int, finishes: tuple[Throw, ...]) -> tuple[Throw, ...] | None:
    """Cherche une sortie en exactement ``depth`` fléchettes."""
    for last in finishes:
        rest = score - last.value
        if rest == 0 and depth == 1:
            return (last,)
        if rest <= 0 or depth == 1:
            continue
        for first in _SETUP:
            gap = rest - first.value
            if gap == 0 and depth == 2:
                return (first, last)
            if gap <= 0 or depth == 2:
                continue
            for second in _SETUP:
                if second.value == gap:
                    return (first, second, last)
    return None
