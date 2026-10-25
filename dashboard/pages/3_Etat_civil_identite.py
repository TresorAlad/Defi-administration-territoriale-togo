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

title, body = nav.ETAT_NAISSANCES
render_section(title, body)
st.plotly_chart(
    style_figure(
        px.line(
            etat_total,
            x="annee",
            y="valeur",
            markers=True,
            labels={"valeur": "Enregistrements", "annee": "Année"},
            **px_defaults(),
        )
    ),
    use_container_width=True,
)

title, body = nav.ETAT_IDENTITE
render_section(title, body)
docs["valeur"] = docs["valeur"].astype(float)
pivot = docs.pivot_table(index="annee", columns="type_document", values="valeur", aggfunc="sum")
st.plotly_chart(
    style_figure(
        px.line(
            docs,
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
st.dataframe(pivot.reset_index(), use_container_width=True, hide_index=True)
