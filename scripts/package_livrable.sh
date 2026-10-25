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

cat > "$WORKDIR/LIREMOI_JURY.md" <<'EOF'
# Livrable Data Challenge - Togo Territoires

## Lancer le dashboard

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas streamlit plotly
cd dashboard
streamlit run app.py
```

Le dossier `data/gold/` contient les marts pre-calcules (39 prefectures, recommandations, inegalites).

## Regenerer le gold (optionnel)

Depot complet requis : bronze, silver, ref, pipeline.
EOF

mkdir -p "$DIST"
(cd "$DIST" && zip -r "${NAME}.zip" "$NAME")
echo "Archive : $DIST/${NAME}.zip"
