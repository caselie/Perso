#!/usr/bin/env bash
# Démarre la borne : serveur local + navigateur en plein écran.
#   ./scripts/run.sh            → serveur + kiosque
#   ./scripts/run.sh --serveur  → serveur seul (utile en développement)
set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${DARTS_PORT:-8080}"
URL="http://127.0.0.1:${PORT}"
cd "$RACINE"

# Environnement virtuel créé au premier lancement.
if [ ! -d .venv ]; then
  echo "→ Création de l'environnement Python…"
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

.venv/bin/python -m app.server --port "$PORT" &
SERVEUR=$!
trap 'kill $SERVEUR 2>/dev/null || true' EXIT INT TERM

# Attente de la disponibilité du serveur.
for _ in $(seq 1 40); do
  if curl -sf -o /dev/null "$URL/api/bootstrap"; then break; fi
  sleep 0.25
done

if [ "${1:-}" = "--serveur" ]; then
  echo "Borne disponible sur $URL (Ctrl+C pour arrêter)"
  wait $SERVEUR
  exit 0
fi

# Premier navigateur disponible, lancé en mode kiosque.
for NAVIGATEUR in chromium chromium-browser google-chrome firefox; do
  if command -v "$NAVIGATEUR" >/dev/null 2>&1; then
    case "$NAVIGATEUR" in
      firefox) "$NAVIGATEUR" --kiosk "$URL" ;;
      *) "$NAVIGATEUR" --kiosk --noerrdialogs --disable-infobars \
           --disable-session-crashed-bubble --disable-pinch \
           --overscroll-history-navigation=0 \
           --user-data-dir="$RACINE/data/navigateur" "$URL" ;;
    esac
    exit 0
  fi
done

echo "Aucun navigateur trouvé. Ouvrez $URL manuellement." >&2
wait $SERVEUR
