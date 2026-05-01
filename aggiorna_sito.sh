#!/bin/bash
# Aggiorna il sito ricette e fa il push su GitHub.
# Uso: ./aggiorna_sito.sh [file.paprikarecipes]

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🍽  Aggiorno il sito ricette..."

# Genera il sito
if [ -n "$1" ]; then
    python3 aggiorna_sito.py "$1"
else
    python3 aggiorna_sito.py
fi

# Push su GitHub
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add docs/ "Backup Paprika/"
    if git diff --cached --quiet; then
        echo "ℹ️  Nessuna modifica da pubblicare."
    else
        git commit -m "Aggiorna ricette — $(date '+%d/%m/%Y %H:%M')"
        git push
        echo "🚀 Sito pubblicato su GitHub Pages!"
    fi
else
    echo "⚠️  Repository git non trovato. Inizializzalo prima con:"
    echo "   git init && git remote add origin https://github.com/TUO-UTENTE/ricette.git"
fi
