# Architecture - Python dashboard

## Faut-il une couche Gold ?

**Oui.** Le silver contient des fichiers propres mais **heterogenes** (niveaux admin implicites, annees differentes, pas de jointures). Le dashboard et le PowerPoint doivent lire des **marts** stables :

- une ligne = un territoire a un niveau donne (region, prefecture, commune, canton)
- indicateurs deja calcules (poids relatif, ratios agences / habitants, ecarts 2010-2022)
- flags qualite (homonymes, decoupage modifie, annee incomplete)

Sans gold, toute la logique serait dupliquee entre Streamlit et le rapport, et les comparaisons 2010/2022 seraient fragiles.

```
Bronze (brut)  -->  Silver (propre)  -->  Gold (metier)  -->  Dashboard + PPT
```

## Sources silver -> usage gold

| Fichier silver | Usage gold |
|----------------|------------|
| `observation-population-decoupage.csv` | Population 2022, hierarchie, poids, inegalites taille communes/cantons |
| `observation-population-hierarchie-2010.csv` | Population 2010 (arbre admin) |
| `observation-acces-electricite.csv` | Taux et abonnes BT par prefecture |
| `agences-ceet.csv`, `agences-tde.csv` | Repartition geographique services publics |
| `observation-enregistrement-etat-civil.csv` | Naissances enregistrees (delai 45 j) |
| `observation-documents-identite.csv` | CNI, passeports, cartes pro |

## Tables Gold prevues

### Dimensions

- **`dim_territoire`** : id, libelle, niveau (`pays`, `region`, `prefecture`, `commune`, `canton`), parent_id, code normalise
- **`dim_temps`** : annee (2010, 2014-2022 selon jeux)

### Faits

- **`fact_population`** : territoire_id, annee, sexe, population
- **`fact_electricite`** : prefecture_id, annee, abonnes_bt, taux_acces_pct
- **`fact_agence`** : agence_id, operateur (CEET/TdE), prefecture_id, commune, geometry, statut
- **`fact_etat_civil`** : annee, sexe, nb_enregistrements
- **`fact_documents_identite`** : annee, type_document, volume

### Marts (dashboard)

- **`mart_profil_prefecture`** : 39 prefectures - pop 2022, poids national, pop 2010 comparable, variation %, taux electricite, nb agences CEET/TdE, habitants par agence
- **`mart_profil_commune`** : communes - population, rang, ratio vs moyenne nationale
- **`mart_inegalites`** : ecarts max/min, concentration Grand Lome, territoires sous-seuil (electricite, agences)
- **`mart_synthese_nationale`** : KPIs pour slide executive

## Defis techniques (traites en gold)

1. **Niveau admin implicite** dans `decoupage_administratif` (TOGO, SAVANES, TONE 1, DAPAONG...) : inference par regles + referentiel `data/ref/` (39 pref, 117 communes).
2. **Homonymes** (`BASSAR (occurrence 2)`) : garder `niveau_decoupage` et ne pas agreger a tort.
3. **2010 vs 2022** : decoupage admin evolue -> colonnes `comparable` / `note_decoupage` sur les faits d'evolution.
4. **Electricite** : prefectures en libelles (LOME, ...) a mapper sur `dim_territoire`.
5. **Agences** : compter par prefecture, calculer ratios avec pop 2022 de la meme prefecture.

## Dashboard (Streamlit)

Pages prevues :

1. **Vue nationale** - KPIs, Grand Lome, inegalites
2. **Profil territorial** - filtres region / prefecture / commune
3. **Demographie** - 2022, pyramide / repartition, taille des communes
4. **Evolution 2010-2022** - avec avertissements decoupage
5. **Services** - electricite + carte agences CEET/TdE
6. **Etat civil et identite** - tendances
7. **Recommandations** - territoires prioritaires (regles metier sur marts)

## Stack Python

- **pandas** : transformations gold
- **pyarrow** : parquet gold (optionnel, plus leger que CSV)
- **streamlit** + **plotly** : dashboard interactif
- **python-pptx** : generation du rapport (phase 2)
