"""Serveur de la borne : API JSON + interface tactile."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .db import DEFAULT_PATH, Database
from .games import catalogue
from .games.base import GameError
from .session import Session
from .throws import InvalidThrow

WEB_ROOT = Path(__file__).resolve().parent.parent / "web"


def create_app(db_path: str | Path = DEFAULT_PATH) -> Flask:
    app = Flask(__name__, static_folder=None)
    db = Database(db_path)
    session = Session(db)

    # ------------------------------------------------------------ interface

    @app.get("/")
    def index():
        return send_from_directory(WEB_ROOT, "index.html")

    @app.get("/static/<path:filename>")
    def assets(filename: str):
        return send_from_directory(WEB_ROOT / "static", filename)

    @app.get("/manifest.webmanifest")
    def manifest():
        return send_from_directory(WEB_ROOT, "manifest.webmanifest")

    # ------------------------------------------------------------------ API

    @app.get("/api/bootstrap")
    def bootstrap():
        return jsonify(
            {
                "games": catalogue(),
                "players": db.players(),
                "match": session.state(),
                "recent": db.recent_matches(10),
            }
        )

    @app.get("/api/players")
    def list_players():
        return jsonify(db.players())

    @app.post("/api/players")
    def create_player():
        name = (request.json or {}).get("name", "")
        return jsonify(db.add_player(name)), 201

    @app.delete("/api/players/<int:player_id>")
    def remove_player(player_id: int):
        db.delete_player(player_id)
        return "", 204

    @app.get("/api/players/<int:player_id>/stats")
    def player_stats(player_id: int):
        try:
            return jsonify(db.player_stats(player_id))
        except KeyError:
            return jsonify({"error": "joueur introuvable"}), 404

    @app.get("/api/matches")
    def recent():
        return jsonify(db.recent_matches(int(request.args.get("limit", 20))))

    @app.get("/api/match")
    def current_match():
        return jsonify(session.state())

    @app.post("/api/match")
    def start_match():
        payload = request.json or {}
        seats = [
            {"id": seat.get("id"), "name": str(seat.get("name", "")).strip() or "Invité"}
            for seat in payload.get("players", [])
        ]
        return jsonify(session.start(payload.get("game", ""), seats, payload.get("options")))

    @app.delete("/api/match")
    def stop_match():
        session.abandon()
        return "", 204

    @app.post("/api/match/throw")
    def register_throw():
        payload = request.json or {}
        try:
            multiplier, sector = int(payload["multiplier"]), int(payload["sector"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "fléchette attendue : multiplier et sector"}), 400
        return jsonify(session.throw(multiplier, sector))

    @app.post("/api/match/undo")
    def undo_throw():
        return jsonify(session.undo())

    # ------------------------------------------------------------- erreurs

    @app.errorhandler(GameError)
    @app.errorhandler(InvalidThrow)
    @app.errorhandler(ValueError)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    app.session = session  # pratique pour les tests
    app.db = db
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Borne de fléchettes")
    parser.add_argument("--host", default=os.environ.get("DARTS_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("DARTS_PORT", 8080)))
    parser.add_argument("--db", default=os.environ.get("DARTS_DB", str(DEFAULT_PATH)))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    create_app(args.db).run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
