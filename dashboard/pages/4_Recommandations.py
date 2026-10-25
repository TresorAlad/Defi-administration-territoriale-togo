import plotly.express as px
import streamlit as st

from lib_gold import load_gold, require_gold
import narratives as nav
from togo_theme import apply_togo_theme, px_defaults, render_hero, render_section, style_figure

apply_togo_theme()
render_hero("Recommandations", "Priorisation territoriale pour rapprocher l'administration des citoyens.")

if not require_gold():
    st.stop()

render_section("Objectif", nav.RECO_INTRO)

reco = load_gold("mart_recommandations.csv")

title, body = nav.RECO_CHART
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.bar(
            reco.head(15),
            x="score_priorite",
            y="prefecture_nom",
            orientation="h",
            color="region_nom",
            labels={"score_priorite": "Score", "prefecture_nom": "Préfecture"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

title, body = nav.RECO_FICHES
render_section(title, body)
for _, row in reco.head(10).iterrows():
    with st.expander(f"{int(row['rang_priorite'])}. {row['prefecture_nom']} — score {row['score_priorite']}"):
        st.write(row["recommandation"])
        st.write(
            f"Population 2022 : {row['population_2022']:,.0f} habitants. "
            f"Taux d'électricité : {row['taux_acces_electricite_pct']} %. "
            f"Agences CEET / TdE : {int(row['nb_agences_ceet'])} / {int(row['nb_agences_tde'])}."
        )

title, body = nav.RECO_PLAN
render_section(title, body)
st.markdown(
    """
1. Renforcer l'électricité dans les préfectures sous la médiane nationale.
2. Ouvrir des guichets CEET ou TdE là où la population est élevée et les points de service absents.
3. Déployer l'état civil mobile dans les zones à faible accès et forte croissance démographique.
4. Mettre à jour les données gold régulièrement pour piloter les investissements.
5. Rééquilibrer les efforts entre le grand Lomé et l'intérieur du pays.
"""
)
