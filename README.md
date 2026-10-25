# Défi administration territoriale - Togo

Tableau de bord **Streamlit** et pipeline de données sur sources ouvertes : recensement (RGPH), accès à l'électricité, agences **CEET** / **TdE**, état civil et documents d'identité.

**Dépôt :** [github.com/TresorAlad/Defi-administration-territoriale-togo](https://github.com/TresorAlad/Defi-administration-territoriale-togo)

## Couches de données

| Couche | Dossier | Rôle |
|--------|---------|------|
| Bronze | `data/bronze/` | Exports bruts (CSV sources) |
| Silver | `data/silver/` | Nettoyage et harmonisation (`data/bronze/clean_data.py`) |
| Ref | `data/ref/` | 39 préfectures, 117 communes, alias et mapping de libellés |
| Gold | `data/gold/` | Marts analytiques prêts pour l'app (`mart_profil_prefecture`, recommandations, etc.) |

Schéma détaillé : [`docs/architecture.md`](docs/architecture.md).

## Installation et commandes

Depuis la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt

# Silver (bronze → silver)
python3 data/bronze/clean_data.py

# Gold (silver + ref → gold)
python3 -m pipeline.gold.build

# Dashboard (local)
streamlit run dashboard/Accueil.py

# Streamlit Cloud : Main file path = dashboard/app.py
```

Le dashboard lit uniquement `data/gold/`. Sans couche gold, l'app affiche un message d'erreur avec les commandes à exécuter.

## Livrables du défi

Les binaires (PDF, PowerPoint, zip) ne sont **pas versionnés** : les générer en local avant remise ou présentation.

```bash
python3 -m pipeline.gold.build

# Dashboard (test des 5 écrans)
streamlit run dashboard/Accueil.py

# Rapports écrits et oral (deps supplémentaires)
pip install -r reports/requirements-report.txt
python3 reports/generate_pdf.py      # → reports/rapport_jury.pdf
python3 reports/generate_pptx.py     # → reports/rapport_jury.pptx (graphiques Plotly)

# Archive légère dashboard + gold
bash scripts/package_livrable.sh     # → dist/livrable_dashboard.zip
```

Documentation des rapports : [`reports/README.md`](reports/README.md).

## Structure utile

| Élément | Chemin |
|---------|--------|
| Accueil Streamlit | `dashboard/Accueil.py`, pages `dashboard/pages/` |
| Charte graphique | `dashboard/CHARTE_GRAPHIQUE.md`, `dashboard/togo_theme.py` |
| Pipeline gold | `pipeline/gold/build.py` |
| Rapports (PDF / PPT) | `reports/generate_pdf.py`, `reports/generate_pptx.py` |
