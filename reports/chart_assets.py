"""Export PNG des graphiques Plotly (meme logique que le dashboard Streamlit)."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD = PROJECT_ROOT / "data" / "gold"
ASSETS = PROJECT_ROOT / "reports" / "assets" / "charts"

TOGO_GREEN = "#006A4E"
TOGO_SEQUENCE = [TOGO_GREEN, "#FFCE00", "#D21034", "#00875A", "#C4A000", "#B91C1C"]
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#1F2937", family="Inter, system-ui, sans-serif"),
    colorway=TOGO_SEQUENCE,
    margin=dict(l=24, r=24, t=48, b=24),
    xaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
    yaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
)


def style_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def px_defaults() -> dict:
    return {"color_discrete_sequence": TOGO_SEQUENCE}


def _export(fig, path: Path, width: int, height: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    style_figure(fig)
    fig.update_layout(
        width=width,
        height=height,
        title=None,
        margin=dict(l=48, r=24, t=24, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.write_image(str(path), scale=2)
    return path


def chart_population_prefectures(mart_pref: pd.DataFrame) -> Path:
    data = mart_pref.sort_values("population_2022")
    h = max(520, len(data) * 22 + 80)
    fig = px.bar(
        data,
        x="population_2022",
        y="prefecture_nom",
        orientation="h",
        labels={"population_2022": "Habitants", "prefecture_nom": "Préfecture"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "demo_population_prefectures.png", 1400, h)


def chart_poids_scatter(mart_pref: pd.DataFrame) -> Path:
    fig = px.scatter(
        mart_pref,
        x="poids_national_pct",
        y="population_2022",
        hover_name="prefecture_nom",
        labels={"poids_national_pct": "Part du Togo (%)", "population_2022": "Habitants"},
        color_discrete_sequence=[TOGO_GREEN],
    )
    return _export(fig, ASSETS / "demo_poids_scatter.png", 1200, 680)


def chart_electricite(mart: pd.DataFrame) -> Path:
    elec = mart.dropna(subset=["taux_acces_electricite_pct"]).sort_values("taux_acces_electricite_pct")
    h = max(520, len(elec) * 22 + 80)
    fig = px.bar(
        elec,
        x="taux_acces_electricite_pct",
        y="prefecture_nom",
        orientation="h",
        color="region_nom",
        labels={"taux_acces_electricite_pct": "Taux (%)", "prefecture_nom": "Préfecture"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "services_electricite.png", 1400, h)


def chart_habitants_par_agence(mart: pd.DataFrame) -> Path:
    hpa = mart[mart["habitants_par_agence"].notna()].sort_values("habitants_par_agence", ascending=False)
    fig = px.bar(
        hpa.head(15),
        x="habitants_par_agence",
        y="prefecture_nom",
        orientation="h",
        labels={"habitants_par_agence": "Habitants / agence", "prefecture_nom": "Préfecture"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "services_habitants_agence.png", 1200, 620)


def _parse_point(wkt: str) -> tuple[float | None, float | None]:
    if not isinstance(wkt, str):
        return None, None
    match = re.search(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", wkt)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def chart_agences_carte(agences: pd.DataFrame) -> Path | None:
    if agences.empty or "geometry_wkt" not in agences.columns:
        return None
    coords = agences["geometry_wkt"].map(_parse_point)
    agences = agences.copy()
    agences["lon"] = coords.map(lambda x: x[0])
    agences["lat"] = coords.map(lambda x: x[1])
    agences = agences.dropna(subset=["lat", "lon"])
    if agences.empty:
        return None
    fig = px.scatter(
        agences,
        x="lon",
        y="lat",
        color_discrete_sequence=[TOGO_GREEN],
        labels={"lon": "Longitude", "lat": "Latitude"},
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85))
    return _export(fig, ASSETS / "services_carte_agences.png", 900, 720)


def chart_naissances(etat: pd.DataFrame) -> Path:
    etat_total = etat[etat["sexe"] == "Total"].copy()
    etat_total["valeur"] = etat_total["valeur"].astype(float)
    etat_total["annee"] = etat_total["annee"].astype(int)
    fig = px.line(
        etat_total,
        x="annee",
        y="valeur",
        markers=True,
        labels={"valeur": "Enregistrements", "annee": "Année"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "etat_naissances.png", 1100, 520)


def chart_documents_identite(docs: pd.DataFrame) -> Path:
    docs = docs.copy()
    docs["valeur"] = docs["valeur"].astype(float)
    fig = px.line(
        docs,
        x="annee",
        y="valeur",
        color="type_document",
        markers=True,
        labels={"valeur": "Nombre", "annee": "Année", "type_document": "Type"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "etat_documents_identite.png", 1100, 520)


def chart_recommandations(reco: pd.DataFrame) -> Path:
    fig = px.bar(
        reco.head(15),
        x="score_priorite",
        y="prefecture_nom",
        orientation="h",
        color="region_nom",
        labels={"score_priorite": "Score de priorité", "prefecture_nom": "Préfecture"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "reco_priorites.png", 1200, 620)


def chart_reco_top5(reco: pd.DataFrame) -> Path:
    fig = px.bar(
        reco.head(5),
        x="score_priorite",
        y="prefecture_nom",
        orientation="h",
        labels={"score_priorite": "Score", "prefecture_nom": "Préfecture"},
        **px_defaults(),
    )
    return _export(fig, ASSETS / "reco_top5_accueil.png", 900, 420)


def export_all_charts() -> dict[str, Path | None]:
    mart = pd.read_csv(GOLD / "mart_profil_prefecture.csv")
    reco = pd.read_csv(GOLD / "mart_recommandations.csv")
    agences = pd.read_csv(GOLD / "fact_agence.csv")
    etat = pd.read_csv(GOLD / "fact_etat_civil.csv")
    docs = pd.read_csv(GOLD / "fact_documents_identite.csv")

    return {
        "pop": chart_population_prefectures(mart),
        "scatter": chart_poids_scatter(mart),
        "elec": chart_electricite(mart),
        "hpa": chart_habitants_par_agence(mart),
        "map": chart_agences_carte(agences),
        "naissances": chart_naissances(etat),
        "identite": chart_documents_identite(docs),
        "reco": chart_recommandations(reco),
        "reco5": chart_reco_top5(reco),
    }
