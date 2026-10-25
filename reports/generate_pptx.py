#!/usr/bin/env python3
"""Genere le PowerPoint jury (10 slides, charte Togo + graphiques dashboard)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD = PROJECT_ROOT / "data" / "gold"
OUT = PROJECT_ROOT / "reports" / "rapport_jury.pptx"

sys.path.insert(0, str(PROJECT_ROOT / "dashboard"))
import narratives as nav  # noqa: E402

from chart_assets import export_all_charts  # noqa: E402
from ppt_theme import (  # noqa: E402
    new_presentation,
    slide_chart,
    slide_chart_and_map,
    slide_conclusion,
    slide_cover,
    slide_kpi_context,
    slide_pipeline,
    slide_recommandations,
    slide_two_charts,
)


def _as_text(value: str | tuple[str, ...]) -> str:
    if isinstance(value, tuple):
        return value[1] if len(value) > 1 else str(value[0])
    return str(value)


def _title(value: str | tuple[str, ...]) -> str:
    if isinstance(value, tuple):
        return str(value[0])
    return value


def main() -> None:
    if not (GOLD / "mart_profil_prefecture.csv").exists():
        raise SystemExit("Couche gold absente. Executer : python3 -m pipeline.gold.build")

    synthese = pd.read_csv(GOLD / "mart_synthese_nationale.csv")
    ineg = pd.read_csv(GOLD / "mart_inegalites.csv")
    reco = pd.read_csv(GOLD / "mart_recommandations.csv")

    kpi = dict(zip(synthese["indicateur"], synthese["valeur"]))
    ineg_d = dict(zip(ineg["indicateur"], ineg["valeur"]))

    charts = export_all_charts()

    part_lome = ineg_d.get("part_grand_lome_golfe_agoe_pct", 0)
    ratio_comm = ineg_d.get("ratio_pop_max_min_commune", 0)
    insight = (
        f"Le Golfe et Agouè-Nyivé concentrent environ {part_lome:.1f} % de la population nationale. "
        f"L'écart entre la commune la plus et la moins peuplée atteint {ratio_comm:.0f} fois : "
        "la décentralisation doit s'appuyer sur des investissements différenciés."
    )

    kpis = [
        ("Population 2022", f"{kpi.get('population_nationale_2022', 0):,.0f}".replace(",", " ")),
        ("Préfectures", str(int(kpi.get("nb_prefectures", 39)))),
        ("Agences CEET", str(int(kpi.get("nb_agences_ceet", 0)))),
        ("Agences TdE", str(int(kpi.get("nb_agences_tde", 0)))),
        ("Écart communes", f"{ratio_comm:.0f}x"),
    ]

    fiches = [
        (str(r["prefecture_nom"]), float(r["score_priorite"]), str(r["recommandation"]))
        for _, r in reco.head(3).iterrows()
    ]

    plan_bullets = [
        "Renforcer l'électricité dans les préfectures sous la médiane nationale.",
        "Ouvrir des guichets CEET ou TdE là où la population est élevée et les points de service absents.",
        "Déployer l'état civil mobile dans les zones à faible accès et forte croissance démographique.",
        "Gold 39/39 : jointures ref + alias open data, pipeline reproductible en deux commandes.",
        "Dashboard Streamlit, rapport PDF et présentation alignés sur les mêmes marts analytiques.",
    ]

    prs = new_presentation()

    slide_cover(
        prs,
        "Territoires et inégalités d'accès au Togo",
        "Data Challenge · Administration territoriale",
        "Données ouvertes consolidées (recensement, électricité, CEET/TdE, état civil, identité) "
        "pour piloter l'action publique au plus près des 117 communes.",
    )
    slide_kpi_context(prs, nav.HOME_INTRO, kpis, insight, 2)
    slide_pipeline(prs, 3)
    slide_chart(
        prs,
        "Démographie",
        _title(nav.DEMO_POP_BARS),
        _as_text(nav.DEMO_POP_BARS),
        charts["pop"],
        4,
    )
    slide_chart(
        prs,
        "Démographie",
        _title(nav.DEMO_SCATTER),
        _as_text(nav.DEMO_SCATTER),
        charts["scatter"],
        5,
    )
    slide_chart(
        prs,
        "Services publics",
        _title(nav.SERVICES_ELEC),
        _as_text(nav.SERVICES_ELEC),
        charts["elec"],
        6,
    )
    slide_chart_and_map(
        prs,
        "Services publics",
        "Proximité des guichets CEET et TdE",
        _as_text(nav.SERVICES_AGENCES) + " " + _as_text(nav.SERVICES_MAP),
        charts["hpa"],
        charts.get("map"),
        7,
    )
    slide_two_charts(
        prs,
        "État civil et identité",
        "Capacité administrative d'enregistrement",
        nav.ETAT_INTRO,
        charts["naissances"],
        charts["identite"],
        8,
    )
    slide_recommandations(prs, charts["reco"], fiches, 9)
    slide_conclusion(prs, plan_bullets, 10)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Rapport genere : {OUT}")
    print(f"Graphiques : {charts['pop'].parent}")


if __name__ == "__main__":
    main()
