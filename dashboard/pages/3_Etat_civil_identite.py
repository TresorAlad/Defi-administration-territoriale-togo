import plotly.express as px
import streamlit as st

from lib_gold import load_gold, require_gold
import narratives as nav
from togo_theme import apply_togo_theme, px_defaults, render_hero, render_section, style_figure

apply_togo_theme()
render_hero("État civil et identité", "Naissances enregistrées et documents d'identité.")

if not require_gold():
    st.stop()

render_section("Objectif", nav.ETAT_INTRO)

etat = load_gold("fact_etat_civil.csv")
docs = load_gold("fact_documents_identite.csv")

etat_total = etat[etat["sexe"] == "Total"].copy()
etat_total["valeur"] = etat_total["valeur"].astype(float)
etat_total["annee"] = etat_total["annee"].astype(int)

years = sorted(etat_total["annee"].unique())
year_range = st.slider(
    "Plage d'années (naissances)",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years))),
    key="etat_year_slider",
)
etat_plot = etat_total[
    (etat_total["annee"] >= year_range[0]) & (etat_total["annee"] <= year_range[1])
]

title, body = nav.ETAT_NAISSANCES
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.line(
            etat_plot,
            x="annee",
            y="valeur",
            markers=True,
            labels={"valeur": "Enregistrements", "annee": "Année"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

docs = docs.copy()
docs["valeur"] = docs["valeur"].astype(float)
doc_types = sorted(docs["type_document"].dropna().unique())
selected_types = st.multiselect(
    "Types de documents affichés",
    doc_types,
    default=doc_types,
    key="doc_types_filter",
)
docs_plot = docs[docs["type_document"].isin(selected_types)]

title, body = nav.ETAT_IDENTITE
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.line(
            docs_plot,
            x="annee",
            y="valeur",
            color="type_document",
            markers=True,
            labels={"valeur": "Nombre", "annee": "Année", "type_document": "Type"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)
pivot = docs_plot.pivot_table(index="annee", columns="type_document", values="valeur", aggfunc="sum")
st.dataframe(pivot.reset_index(), use_container_width=True, hide_index=True)

render_section(*nav.LIMITES_ANALYSE)
