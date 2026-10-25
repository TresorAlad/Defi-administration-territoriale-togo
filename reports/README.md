# Rapports du défi

Maximum **10 sections** (PowerPoint ou PDF), alignées sur les marts gold.

## PDF

```bash
pip install -r reports/requirements-report.txt
python3 -m pipeline.gold.build
python3 reports/generate_pdf.py
```

Fichier produit : `reports/rapport_jury.pdf`

## PowerPoint (10 slides)

Mise en page 16:9 (bandeau tricolore, cartes KPI, textes `narratives.py`) et **graphiques Plotly identiques au dashboard** exportés en PNG (kaleido).

```bash
pip install -r reports/requirements-report.txt
python3 -m pipeline.gold.build
python3 reports/generate_pptx.py
```

Fichiers produits :

- `reports/rapport_jury.pptx` (~1 Mo, visuels intégrés)
- `reports/assets/charts/*.png` (régénérables, cache local)

## Contenu

1. Contexte et problématique
2. Méthodologie (bronze / silver / ref / gold)
3. Démographie 2022
4. Évolution 2010-2022
5. Électricité et agences CEET / TdE
6. État civil et identité
7. Recommandations prioritaires
8. Conclusion
