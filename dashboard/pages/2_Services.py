import re

import plotly.express as px
import streamlit as st

from lib_gold import load_gold, require_gold
import narratives as nav
from togo_theme import apply_togo_theme, px_defaults, render_hero, render_section, style_figure

apply_togo_theme()
render_hero("Services publics", "Électricité et agences CEET / Togolaise des eaux.")

if not require_gold():
    st.stop()

render_section("Objectif", nav.SERVICES_INTRO)

mart = load_gold("mart_profil_prefecture.csv")
agences = load_gold("fact_agence.csv")


def parse_point(wkt: str) -> tuple[float | None, float | None]:
    if not isinstance(wkt, str):
        return None, None
    match = re.search(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", wkt)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


if not agences.empty and "geometry_wkt" in agences.columns:
    coords = agences["geometry_wkt"].map(parse_point)
    agences["lon"] = coords.map(lambda x: x[0])
    agences["lat"] = coords.map(lambda x: x[1])
    agences = agences.dropna(subset=["lat", "lon"])

title, body = nav.SERVICES_ELEC
render_section(title, body)
elec = mart.dropna(subset=["taux_acces_electricite_pct"]).sort_values("taux_acces_electricite_pct")
st.plotly_chart(
    style_figure(
        px.bar(
            elec,
            x="taux_acces_electricite_pct",
            y="prefecture_nom",
            orientation="h",
            color="region_nom",
            labels={"taux_acces_electricite_pct": "Taux (%)", "prefecture_nom": "Préfecture"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

title, body = nav.SERVICES_AGENCES
render_section(title, body)
hpa = mart[mart["habitants_par_agence"].notna()].sort_values("habitants_par_agence", ascending=False)
st.plotly_chart(
    style_figure(
        px.bar(
            hpa.head(15),
            x="habitants_par_agence",
            y="prefecture_nom",
            orientation="h",
            labels={"habitants_par_agence": "Habitants / agence", "prefecture_nom": "Préfecture"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

title, body = nav.SERVICES_MAP
render_section(title, body)
if agences.empty:
    st.warning("Géométrie indisponible.")
else:
    st.map(agences[["lat", "lon"]], size=20, color="#006A4E")
    st.dataframe(
        agences[["operateur", "etablissement", "prefecture", "commune", "statut_activite"]].head(50),
        use_container_width=True,
        hide_index=True,
    )

zero_agence = mart[(mart["nb_agences_total"] == 0) & (mart["population_2022"] > 50000)]
if not zero_agence.empty:
    st.warning(
        "Préfectures de plus de 50 000 habitants sans agence recensée : "
        + ", ".join(zero_agence["prefecture_nom"].tolist())
    )
