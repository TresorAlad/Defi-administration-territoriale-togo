import plotly.express as px
import streamlit as st

from filters import select_region
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

region, filtered = select_region(mart_pref, key="demo_region")

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

title, body = nav.DEMO_POIDS
render_section(title, body)
poids = filtered.nlargest(12, "poids_national_pct").sort_values("poids_national_pct")
st.plotly_chart(
    style_figure(
        px.bar(
            poids,
            x="poids_national_pct",
            y="prefecture_nom",
            orientation="h",
            labels={"poids_national_pct": "Part du Togo (%)", "prefecture_nom": "Préfecture"},
            color_discrete_sequence=[TOGO_GREEN],
        )
    ),
    use_container_width=True,
)

title, body = nav.DEMO_EVOL
render_section(title, body)
evol_ok = evol[evol["comparable_decoupage"] == "oui"].copy()
if region != "Toutes":
    evol_ok = evol_ok[evol_ok["region_nom"] == region]
evol_ok = evol_ok.sort_values("variation_pct", ascending=False)

title_c, body_c = nav.DEMO_EVOL_CHART
render_section(title_c, body_c)
if evol_ok.empty:
    st.info("Aucune préfecture comparable pour cette région.")
else:
    st.plotly_chart(
        style_figure(
            px.bar(
                evol_ok.head(12),
                x="variation_pct",
                y="prefecture_nom",
                orientation="h",
                labels={"variation_pct": "Variation (%)", "prefecture_nom": "Préfecture"},
                color_discrete_sequence=[TOGO_GREEN],
            )
        ),
        use_container_width=True,
    )
    st.caption(f"{len(evol_ok)} préfectures comparables affichées (découpage stable 2010-2022).")
    st.dataframe(
        evol_ok[
            ["prefecture_nom", "region_nom", "population_2010", "population_2022", "variation_pct"]
        ],
        use_container_width=True,
        hide_index=True,
    )

title, body = nav.DEMO_COMMUNES
render_section(title, body)
com_filtered = mart_com
if region != "Toutes":
    pref_in_region = filtered["prefecture_nom"].tolist()
    com_filtered = mart_com[mart_com["prefecture_nom"].isin(pref_in_region)]
top = com_filtered.nlargest(10, "population_2022")
bottom = com_filtered.nsmallest(10, "population_2022")
c1, c2 = st.columns(2)
c1.markdown("**Plus peuplées**")
c1.dataframe(top[["commune_nom", "prefecture_nom", "population_2022"]], hide_index=True)
c2.markdown("**Moins peuplées**")
c2.dataframe(bottom[["commune_nom", "prefecture_nom", "population_2022"]], hide_index=True)

render_section(*nav.LIMITES_ANALYSE)
