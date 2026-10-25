#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
NAME="livrable_dashboard"
WORKDIR="$DIST/$NAME"

rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

cp -r "$ROOT/dashboard" "$WORKDIR/"
cp -r "$ROOT/data/gold" "$WORKDIR/data/"
mkdir -p "$WORKDIR/data/ref"
cp "$ROOT/data/ref/alias_open_data.csv" "$WORKDIR/data/ref/"
cp "$ROOT/requirements.txt" "$WORKDIR/"
cp "$ROOT/README.md" "$WORKDIR/"

cat > "$WORKDIR/LIREMOI.md" <<'EOF'
# Défi administration territoriale - Togo

## Lancer le dashboard

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/Accueil.py
```

Le dossier `data/gold/` contient les marts pré-calculés (39 préfectures, recommandations, inégalités).

## Régénérer le gold (optionnel)

Dépôt complet requis : bronze, silver, ref, pipeline.
EOF

mkdir -p "$DIST"
(cd "$DIST" && zip -r "${NAME}.zip" "$NAME")
echo "Archive : $DIST/${NAME}.zip"
