"""Persistance SQLite : joueurs, parties, statistiques.

Une seule base fichier, aucune dépendance externe : la borne doit pouvoir
tourner hors ligne et redémarrer sans rien perdre.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "raspydarts.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    id          INTEGER PRIMARY KEY,
    game        TEXT NOT NULL,
    options     TEXT NOT NULL,
    seats       TEXT NOT NULL,
    history     TEXT NOT NULL,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    winner_seat INTEGER
);

CREATE TABLE IF NOT EXISTS results (
    match_id    INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    seat        INTEGER NOT NULL,
    player_id   INTEGER REFERENCES players(id) ON DELETE SET NULL,
    name        TEXT NOT NULL,
    won         INTEGER NOT NULL,
    stats       TEXT NOT NULL,
    PRIMARY KEY (match_id, seat)
);

CREATE INDEX IF NOT EXISTS results_player ON results(player_id);
CREATE INDEX IF NOT EXISTS matches_open ON matches(finished_at);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path | str = DEFAULT_PATH):
        self.path = Path(path)
        if self.path.parent != Path("."):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, timeout=5)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    # -------------------------------------------------------------- joueurs

    def players(self) -> list[dict]:
        with self.connect() as con:
            rows = con.execute(
                """SELECT p.id, p.name, COUNT(r.match_id) AS matches,
                          COALESCE(SUM(r.won), 0) AS wins
                     FROM players p
                     LEFT JOIN results r ON r.player_id = p.id
                    GROUP BY p.id
                    ORDER BY p.name COLLATE NOCASE"""
            ).fetchall()
        return [dict(row) for row in rows]

    def add_player(self, name: str) -> dict:
        name = name.strip()
        if not name:
            raise ValueError("le nom du joueur est vide")
        if len(name) > 24:
            raise ValueError("le nom du joueur ne doit pas dépasser 24 caractères")
        with self.connect() as con:
            existing = con.execute(
                "SELECT id, name FROM players WHERE name = ?", (name,)
            ).fetchone()
            if existing:
                return {"id": existing["id"], "name": existing["name"]}
            cur = con.execute(
                "INSERT INTO players (name, created_at) VALUES (?, ?)", (name, now())
            )
        return {"id": cur.lastrowid, "name": name}

    def delete_player(self, player_id: int) -> None:
        with self.connect() as con:
            con.execute("DELETE FROM players WHERE id = ?", (player_id,))

    # -------------------------------------------------------------- parties

    def create_match(self, game: str, options: dict, seats: list[dict]) -> int:
        with self.connect() as con:
            cur = con.execute(
                """INSERT INTO matches (game, options, seats, history, started_at)
                   VALUES (?, ?, ?, '[]', ?)""",
                (game, json.dumps(options), json.dumps(seats), now()),
            )
        return int(cur.lastrowid)

    def save_history(self, match_id: int, history: list[dict]) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE matches SET history = ? WHERE id = ?",
                (json.dumps(history), match_id),
            )

    def finish_match(
        self, match_id: int, winner_seat: int | None, seats: list[dict], stats: list[dict]
    ) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE matches SET finished_at = ?, winner_seat = ? WHERE id = ?",
                (now(), winner_seat, match_id),
            )
            con.executemany(
                """INSERT OR REPLACE INTO results
                       (match_id, seat, player_id, name, won, stats)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        match_id,
                        seat_index,
                        seat.get("id"),
                        seat["name"],
                        int(seat_index == winner_seat),
                        json.dumps(stats[seat_index]),
                    )
                    for seat_index, seat in enumerate(seats)
                ],
            )

    def abandon_match(self, match_id: int) -> None:
        with self.connect() as con:
            con.execute("DELETE FROM matches WHERE id = ? AND finished_at IS NULL", (match_id,))

    def open_match(self) -> dict | None:
        """Dernière partie non terminée, pour reprendre après un redémarrage."""
        with self.connect() as con:
            row = con.execute(
                """SELECT * FROM matches WHERE finished_at IS NULL
                    ORDER BY id DESC LIMIT 1"""
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "game": row["game"],
            "options": json.loads(row["options"]),
            "seats": json.loads(row["seats"]),
            "history": json.loads(row["history"]),
        }

    def recent_matches(self, limit: int = 20) -> list[dict]:
        with self.connect() as con:
            rows = con.execute(
                """SELECT m.id, m.game, m.finished_at, m.winner_seat, m.seats
                     FROM matches m
                    WHERE m.finished_at IS NOT NULL
                    ORDER BY m.id DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        matches = []
        for row in rows:
            seats = json.loads(row["seats"])
            winner = row["winner_seat"]
            matches.append(
                {
                    "id": row["id"],
                    "game": row["game"],
                    "finished_at": row["finished_at"],
                    "players": [seat["name"] for seat in seats],
                    "winner": seats[winner]["name"] if winner is not None else None,
                }
            )
        return matches

    # --------------------------------------------------------- statistiques

    def player_stats(self, player_id: int) -> dict:
        with self.connect() as con:
            player = con.execute(
                "SELECT id, name FROM players WHERE id = ?", (player_id,)
            ).fetchone()
            if player is None:
                raise KeyError(player_id)
            rows = con.execute(
                """SELECT m.game, r.won, r.stats, m.finished_at
                     FROM results r JOIN matches m ON m.id = r.match_id
                    WHERE r.player_id = ?
                    ORDER BY m.id DESC""",
                (player_id,),
            ).fetchall()

        par_jeu: dict[str, dict] = defaultdict(
            lambda: {"matches": 0, "wins": 0, "darts": 0, "points": 0}
        )
        records = {
            "average3": 0.0,
            "mpr": 0.0,
            "best_checkout": 0,
            "count_180": 0,
            "best_leg": None,
        }
        totaux = Counter()

        for row in rows:
            stats = json.loads(row["stats"])
            bucket = par_jeu[row["game"]]
            bucket["matches"] += 1
            bucket["wins"] += row["won"]
            bucket["darts"] += stats.get("darts", 0)
            bucket["points"] += stats.get("points", 0)
            totaux["matches"] += 1
            totaux["wins"] += row["won"]
            totaux["darts"] += stats.get("darts", 0)
            totaux["count_180"] += stats.get("count_180", 0)

            records["average3"] = max(records["average3"], stats.get("average3", 0.0))
            records["mpr"] = max(records["mpr"], stats.get("mpr", 0.0))
            records["best_checkout"] = max(
                records["best_checkout"], stats.get("best_checkout", 0)
            )
            leg = stats.get("best_leg")
            if leg and (records["best_leg"] is None or leg < records["best_leg"]):
                records["best_leg"] = leg

        records["count_180"] = totaux["count_180"]
        for bucket in par_jeu.values():
            bucket["average3"] = (
                round(bucket["points"] / bucket["darts"] * 3, 2) if bucket["darts"] else 0.0
            )

        return {
            "id": player["id"],
            "name": player["name"],
            "matches": totaux["matches"],
            "wins": totaux["wins"],
            "win_pct": (
                round(totaux["wins"] / totaux["matches"] * 100, 1) if totaux["matches"] else 0.0
            ),
            "records": records,
            "by_game": dict(par_jeu),
        }
