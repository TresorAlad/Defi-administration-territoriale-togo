# Charte graphique - Dashboard Togo

## Principe

- **Primaire : blanc** (`#FFFFFF`) - fond app, cartes KPI, graphiques Plotly.
- **Accents drapeau** : vert `#006A4E`, jaune `#FFCE00`, rouge `#D21034`.
- **Texte** : `#1F2937` (titres), `#6B7280` (secondaire).

## Fichiers

| Fichier | Role |
|---------|------|
| `.streamlit/config.toml` | Theme Streamlit natif (fond blanc) |
| `togo_theme.py` | CSS, hero bande tricolore, helpers Plotly |

## Lancer

```bash
cd dashboard
streamlit run app.py
```

Les couleurs des graphiques passent par `px_defaults()` et `style_figure()`.

## Narration

Les textes pédagogiques sont centralisés dans `narratives.py` et affichés via `render_section()` avant chaque visuel.
