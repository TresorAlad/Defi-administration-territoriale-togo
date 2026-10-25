# Défi administration territoriale - Togo

Tableau de bord Python sur données ouvertes (recensement, électricité, état civil, identité, agences CEET/TdE).

Dépôt : [github.com/TresorAlad/Defi-administration-territoriale-togo](https://github.com/TresorAlad/Defi-administration-territoriale-togo)

## Couches de donnees

| Couche | Dossier | Role |
|--------|---------|------|
| Bronze | `data/bronze/` | Exports bruts (CSV source) |
| Silver | `data/silver/` | Nettoyage, harmonisation (`clean_data.py`) |
| Ref | `data/ref/` | 39 prefectures, 117 communes, mapping libelles |
| Gold | `data/gold/` | **Pret pour l'app** : `mart_profil_prefecture`, etc. |

## Commandes

```bash
# Silver (bronze -> silver)
python data/bronze/clean_data.py

# Gold (silver -> gold)
python -m pipeline.gold.build

# Dashboard
streamlit run dashboard/app.py
```

## Livrables concours (Badge Or)

```bash
python3 -m pipeline.gold.build
cd dashboard && streamlit run app.py
python3 reports/generate_pptx.py          # pip install python-pptx
bash scripts/package_livrable.sh          # dist/livrable_dashboard.zip
```

Voir `docs/strategie_badge_or.md` pour le pitch jury.

Voir `docs/architecture.md` pour le detail des tables gold et des ecrans.
