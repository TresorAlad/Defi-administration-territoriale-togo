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
pip install -r requirements.txt

# Silver (bronze -> silver)
python3 data/bronze/clean_data.py

# Gold (silver -> gold)
python3 -m pipeline.gold.build

# Dashboard (depuis la racine du depot)
streamlit run dashboard/app.py
```

## Deploiement Streamlit Community Cloud

1. Pousser le code sur GitHub (branche `main`).
2. Aller sur [share.streamlit.io](https://share.streamlit.io/), se connecter avec GitHub.
3. **New app** : repository `TresorAlad/Defi-administration-territoriale-togo`.
4. **Main file path** : `dashboard/app.py`
5. **Branch** : `main` puis **Deploy**.

**GitHub URL (deploy manuel)** :  
`https://github.com/TresorAlad/Defi-administration-territoriale-togo/blob/main/dashboard/app.py`

Dependances : uniquement `requirements.txt` (pas de `pyproject.toml`, sinon erreur Poetry sur Cloud).

Apres un push : **Manage app → Reboot app**.

## Livrables concours (Badge Or)

```bash
python3 -m pipeline.gold.build
cd dashboard && streamlit run app.py
python3 reports/generate_pdf.py           # pip install -r reports/requirements-report.txt
python3 reports/generate_pptx.py
bash scripts/package_livrable.sh          # dist/livrable_dashboard.zip
```

Voir `docs/architecture.md` pour le detail des tables gold et des ecrans.

Les rapports PDF/PPT et le zip livrable ne sont pas versionnes : les generer localement avant depot concours.
