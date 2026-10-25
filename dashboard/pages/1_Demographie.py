import plotly.express as px
import streamlit as st

from lib_gold import load_gold, require_gold
import narratives as nav
from togo_theme import TOGO_GREEN, apply_togo_theme, px_defaults, render_hero, render_section, style_figure

apply_togo_theme()
render_hero("Démographie", "Population 2022 et évolution depuis 2010.")

if not require_gold():
    st.stop()

render_section("Objectif", nav.DEMO_INTRO)

mart_pref = load_gold("mart_profil_prefecture.csv")
mart_com = load_gold("mart_profil_commune.csv")
evol = load_gold("mart_evolution_2010_2022.csv")

region = st.selectbox(
    "Région",
    ["Toutes"] + sorted(mart_pref["region_nom"].dropna().unique()),
)
filtered = mart_pref if region == "Toutes" else mart_pref[mart_pref["region_nom"] == region]

title, body = nav.DEMO_POP_BARS
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.bar(
            filtered.sort_values("population_2022"),
            x="population_2022",
            y="prefecture_nom",
            orientation="h",
            labels={"population_2022": "Habitants", "prefecture_nom": "Préfecture"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

title, body = nav.DEMO_SCATTER
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.scatter(
            filtered,
            x="poids_national_pct",
            y="population_2022",
            hover_name="prefecture_nom",
            labels={"poids_national_pct": "Part du Togo (%)", "population_2022": "Habitants"},
            color_discrete_sequence=[TOGO_GREEN],
        )
    ),
    use_container_width=True,
)

title, body = nav.DEMO_EVOL
render_section(title, body)
evol_ok = evol[evol["comparable_decoupage"] == "oui"].sort_values("variation_pct", ascending=False)
st.caption(f"{len(evol_ok)} préfectures comparables sur 39.")
st.dataframe(
    evol_ok[
        ["prefecture_nom", "region_nom", "population_2010", "population_2022", "variation_pct"]
    ],
    use_container_width=True,
    hide_index=True,
)

title, body = nav.DEMO_COMMUNES
render_section(title, body)
top = mart_com.nlargest(10, "population_2022")
bottom = mart_com.nsmallest(10, "population_2022")
c1, c2 = st.columns(2)
c1.dataframe(top[["commune_nom", "prefecture_nom", "population_2022"]], hide_index=True)
c2.dataframe(bottom[["commune_nom", "prefecture_nom", "population_2022"]], hide_index=True)
