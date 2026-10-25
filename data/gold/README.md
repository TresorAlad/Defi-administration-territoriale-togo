# Couche Gold (pret pour le dashboard)

Generee par :

```bash
python3 -m pipeline.gold.build
```

Sources : `data/silver/` + `data/ref/`.

## Fichiers principaux pour l'application

| Fichier | Usage app |
|---------|-----------|
| `mart_profil_prefecture.csv` | 1 ligne / prefecture : pop, poids %, electricite, agences |
| `mart_profil_commune.csv` | 1 ligne / commune |
| `mart_inegalites.csv` | KPIs concours (ratio communes, Grand Lome, etc.) |
| `mart_synthese_nationale.csv` | Bandeau accueil |
| `dim_territoire.csv` | Annuaire region / prefecture / commune (161 lignes) |

Les `fact_*.csv` servent au detail et aux prochaines pages (2010-2022, etat civil, identite).

Le dashboard Streamlit lit **surtout les `mart_*`**.
