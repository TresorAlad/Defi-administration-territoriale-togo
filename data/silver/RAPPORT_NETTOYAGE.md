# Rapport de nettoyage - ingestion

Sources brutes : dossier `ingestion/` (fichiers d'origine inchanges).

Sortie : dossier `ingestion/clean/` generee par `python3 ingestion/clean_data.py`.

## Fichiers produits

| Fichier clean | Source | Role |
|---------------|--------|------|
| `schema-ceet.csv` | `schema-ceet.csv` | Metadonnees formulaire (204 champs) |
| `schema-togolaise-des-eaux-tde.csv` | `schema-togolaise-des-eaux-tde.csv` | Idem TDE |
| `agences-ceet.csv` | `file-agences-ceet-*.csv` | Agences CEET (34 lignes) |
| `agences-tde.csv` | `file-agences-tde-*.csv` | Agences TDE (59 lignes) |
| `observation-documents-identite.csv` | `observationdata-fsemhj.csv` | Production CNI / passeports |
| `observation-population-decoupage.csv` | `observationdata-kwwolwb.csv` | Population 2022 par zone |
| `observation-acces-electricite.csv` | `observationdata-puncgpd.csv` | Acces electricite |
| `observation-population-hierarchie-2010.csv` | `observationdata-sapxctg.csv` | Population 2010 (arbre admin) |
| `observation-enregistrement-etat-civil.csv` | `observationdata-vrsicxf.csv` | Naissances enregistrees |
| `manifest.json` | - | Stats par fichier |

## Regles appliquees

### Communes a tous les jeux

- Trim des espaces en debut / fin.
- Espaces multiples reduits a un seul.
- Apostrophes typographiques unifiees en `'`.
- Encodage de sortie : UTF-8 sans BOM.

### Agences CEET / TDE

- `Nsp`, `N/a`, `Néant` (et variantes) -> cellule vide (NULL logique).
- Valeurs entre accolades `{Lundi,Mardi,...}` -> `Lundi; Mardi; ...` (plus simple en SQL).
- Colonnes renommees en noms lisibles (`etablissement`, `localite`, `geometry_wkt`, etc.).

### Population decoupage (kwwolwb)

- 13 libelles administratifs en double (ex. deux lignes `BASSAR` avec des effectifs differents).
- Strategie : **ne pas fusionner** (risque d'erreur). La 2e occurrence et suivantes deviennent `NOM (occurrence 2)` avec colonnes `decoupage_source`, `occurrence`, `niveau_decoupage`, `ligne_source`.

### Documents identite (fsemhj)

- Colonne `annee_incomplete=oui` pour 2021 (source : Passeports seulement, pas de TOTAL ni CNI).

### Population hierarchie 2010 (sapxctg)

- Colonne `Unit` vide en source -> remplie avec `Nombre`.
- En-tete harmonise : `indicateur` (singulier).

### Etat civil (vrsicxf)

- Correction `Tota` -> `Total`.

### Non modifie

- `adf-togo-data-pipeli_migration_analysis.csv` (meta pipeline ADF).

## Relancer le nettoyage

```bash
cd "/home/tresor/Administration defis"
python3 ingestion/clean_data.py
```
