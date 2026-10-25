# Rapports jury

Maximum **10 sections** (PowerPoint ou PDF), alignees sur les marts gold.

## PDF (recommande pour remise)

```bash
pip install -r reports/requirements-report.txt
python3 -m pipeline.gold.build
python3 reports/generate_pdf.py
```

Fichier produit : `reports/rapport_jury.pdf`

## PowerPoint (10 slides jury)

Mise en page 16:9 (bandeau tricolore, cartes KPI, textes `narratives.py`) et **graphiques Plotly identiques au dashboard** exportes en PNG (kaleido).

```bash
pip install -r reports/requirements-report.txt
python3 -m pipeline.gold.build
python3 reports/generate_pptx.py
```

Fichiers produits :

- `reports/rapport_jury.pptx` (~1 Mo, visuels integres)
- `reports/assets/charts/*.png` (regenerables, cache local)

## Contenu

1. Contexte et problematique
2. Methodologie (bronze / silver / ref / gold)
3. Demographie 2022
4. Evolution 2010-2022
5. Electricite et agences CEET / TdE
6. Etat civil et identite
7. Recommandations prioritaires
8. Conclusion
