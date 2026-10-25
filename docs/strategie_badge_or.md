# Strategie Badge Or - Data Challenge

## Ce que le jury recompense

| Critere Badge Or | Notre reponse |
|------------------|---------------|
| Maitrise totale de la donnee | Pipeline Bronze -> Silver -> Ref -> Gold + manifest + alias documentes |
| Analyse percutante | Inegalites quantifiees (35x communes, 27 % Grand Lome, ecarts electricite) |
| Visualisation fluide | Streamlit multi-pages, Plotly, carte agences |
| Recommandations exploitables | `mart_recommandations.csv` + page dediee + PPT slide 9 |

## Livrables concours

1. **Zip dashboard** : `scripts/package_livrable.sh` -> `dist/livrable_dashboard.zip`
2. **PowerPoint** : `python3 reports/generate_pptx.py` -> `reports/rapport_jury.pptx` (10 slides)

## Pitch oral (2 minutes)

1. Probleme : decentralisation + 117 communes inegales + acces services heterogene.
2. Methode : 4 couches, referentiel admin 39/117, gold 39/39 joint.
3. Chiffre choc : ratio 35x entre communes, Grand Lome ~27 % pop.
4. Action : top 3 prefectures `mart_recommandations` avec mesures concretes.
5. Reproductibilite : 2 commandes regenent tout le gold.

## Checklist avant soumission

- [ ] `python3 data/bronze/clean_data.py`
- [ ] `python3 -m pipeline.gold.build`
- [ ] `streamlit run dashboard/app.py` (tester 5 ecrans)
- [ ] `python3 reports/generate_pptx.py`
- [ ] Zip livrable + README jury dans le depot
- [ ] Relire accents FR (UI + PPT)
- [ ] Preparer reponse jury : limites 2010/2022 decoupage, Agoue-Nyive >100 % electricite (source)

## Se differencier des autres equipes

- **Ref + alias** : pas seulement des graphiques, une vraie jointure territoriale.
- **Score de priorite** : pas des recommandations generiques.
- **Tracabilite** : silver flags (homonymes, 2021 incomplete) mentionnes dans l'app.
