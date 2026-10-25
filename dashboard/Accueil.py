"""Tableau de bord - Administration des défis (couche gold)."""

import plotly.express as px
import streamlit as st

from lib_gold import load_gold, require_gold
import narratives as nav
from togo_theme import apply_togo_theme, px_defaults, render_hero, render_lead, render_section, style_figure

st.set_page_config(
    page_title="Territoires Togo - Accès aux services",
    page_icon="🇹🇬",
    layout="wide",
)

apply_togo_theme()
render_hero(
    "Profils territoriaux et inégalités d'accès",
    "Données ouvertes consolidées pour le pilotage territorial.",
)

if not require_gold():
    st.stop()

render_section("Bienvenue", nav.HOME_INTRO)

synthese = load_gold("mart_synthese_nationale.csv")
inegalites = load_gold("mart_inegalites.csv")
reco = load_gold("mart_recommandations.csv")

kpi = {r["indicateur"]: r["valeur"] for _, r in synthese.iterrows()}
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Population 2022", f"{kpi.get('population_nationale_2022', 0):,.0f}".replace(",", " "))
c2.metric("Préfectures", int(kpi.get("nb_prefectures", 39)))
c3.metric("Agences CEET", int(kpi.get("nb_agences_ceet", 0)))
c4.metric("Agences TdE", int(kpi.get("nb_agences_tde", 0)))
ratio = inegalites.loc[inegalites["indicateur"] == "ratio_pop_max_min_commune", "valeur"]
c5.metric("Écart communes (max/min)", f"{ratio.iloc[0]:.0f}x" if len(ratio) else "-")

render_lead(nav.HOME_KPI)

part_lome = inegalites.loc[inegalites["indicateur"] == "part_grand_lome_golfe_agoe_pct", "valeur"]
if len(part_lome) and len(ratio):
    st.info(
        f"Golfe et Agouè-Nyivé concentrent environ {part_lome.iloc[0]:.1f} % de la population. "
        f"L'écart entre la commune la plus et la moins peuplée atteint {ratio.iloc[0]:.0f} fois."
    )

title, body = nav.RECO_CHART
render_section(title, body)
fig = px.bar(
    reco.head(5),
    x="score_priorite",
    y="prefecture_nom",
    orientation="h",
    title="Cinq préfectures en tête de priorité",
    labels={"score_priorite": "Score", "prefecture_nom": "Préfecture"},
    **px_defaults(),
)
st.plotly_chart(style_figure(fig), use_container_width=True)

render_section(*nav.CONCLUSIONS_CLE)
