#!/usr/bin/env python3
"""Genere le rapport PDF du defi (10 pages) depuis data/gold/."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD = PROJECT_ROOT / "data" / "gold"
OUT = PROJECT_ROOT / "reports" / "rapport_jury.pdf"

TOGO_GREEN = colors.HexColor("#006A4E")
TOGO_YELLOW = colors.HexColor("#FFCE00")
TOGO_RED = colors.HexColor("#D21034")
TOGO_INK = colors.HexColor("#1F2937")
TOGO_MUTED = colors.HexColor("#6B7280")


def load_gold() -> tuple[dict, dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    synthese = pd.read_csv(GOLD / "mart_synthese_nationale.csv")
    ineg = pd.read_csv(GOLD / "mart_inegalites.csv")
    reco = pd.read_csv(GOLD / "mart_recommandations.csv")
    evol = pd.read_csv(GOLD / "mart_evolution_2010_2022.csv")
    pref = pd.read_csv(GOLD / "mart_profil_prefecture.csv")
    kpi = dict(zip(synthese["indicateur"], synthese["valeur"]))
    ineg_d = dict(zip(ineg["indicateur"], ineg["valeur"]))
    return kpi, ineg_d, reco, evol, pref


def build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Heading1"],
            fontSize=22,
            textColor=TOGO_INK,
            spaceAfter=14,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=12,
            textColor=TOGO_MUTED,
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=16,
            textColor=TOGO_GREEN,
            spaceBefore=8,
            spaceAfter=10,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=11,
            textColor=TOGO_INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=11,
            textColor=TOGO_INK,
            leftIndent=12,
            spaceAfter=4,
        ),
        "th": ParagraphStyle(
            "TableHead",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.white,
            fontName="Helvetica-Bold",
            leading=11,
        ),
        "td": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontSize=8,
            textColor=TOGO_INK,
            leading=11,
            spaceAfter=0,
            spaceBefore=0,
        ),
        "td_center": ParagraphStyle(
            "TableCellCenter",
            parent=base["Normal"],
            fontSize=8,
            textColor=TOGO_INK,
            leading=11,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
        ),
    }


def cell_para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)), style)


def bullet_list(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(text, style), leftIndent=12) for text in items],
        bulletType="bullet",
        start="•",
    )


def stripe_table(width: float) -> Table:
    data = [[""]]
    table = Table(data, colWidths=[width], rowHeights=[6])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), TOGO_GREEN),
                ("LINEBELOW", (0, 0), (0, 0), 2, TOGO_YELLOW),
            ]
        )
    )
    return table


def main() -> None:
    kpi, ineg_d, reco, evol, pref = load_gold()
    styles = build_styles()
    story: list = []

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Territoires et inegalites d'acces - Togo",
        author="Defi administration territoriale",
    )
    width = doc.width

    # 1 - Couverture
    story.append(stripe_table(width))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("Territoires et inégalités d'accès au Togo", styles["title"]))
    story.append(
        Paragraph(
            "Défi administration territoriale - Profils territoriaux, pipeline de données et recommandations",
            styles["subtitle"],
        )
    )
    story.append(
        Paragraph(
            "Dashboard Streamlit, couche gold (39 préfectures, 117 communes), "
            "données ouvertes : recensement, électricité, agences CEET/TdE, état civil, identité.",
            styles["body"],
        )
    )
    story.append(PageBreak())

    # 2 - Contexte
    story.append(Paragraph("1. Contexte et enjeux", styles["h2"]))
    story.append(
        bullet_list(
            [
                "39 préfectures et 117 communes aux poids démographiques très inégaux.",
                f"Grand Lomé (Golfe + Agouè-Nyivé) : {ineg_d.get('part_grand_lome_golfe_agoe_pct', 0):.1f} % de la population.",
                f"Écart max/min entre communes : {ineg_d.get('ratio_pop_max_min_commune', 0):.0f} fois.",
                "Objectif : rapprocher l'administration des citoyens grâce à la donnée.",
            ],
            styles["bullet"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # 3 - Methodologie
    story.append(Paragraph("2. Méthodologie", styles["h2"]))
    story.append(
        bullet_list(
            [
                "Bronze : exports bruts | Silver : nettoyage | Ref : référentiel admin et alias.",
                "Gold : marts analytiques, scores et recommandations par préfecture.",
                "Pipeline : clean_data.py et pipeline.gold.build.",
                "Limites : homonymes RGPH, évolution 2010-2022 selon découpage.",
            ],
            styles["bullet"],
        )
    )
    story.append(PageBreak())

    # 4 - Demographie
    pop_nat = kpi.get("population_nationale_2022", 0)
    story.append(Paragraph("3. Démographie 2022", styles["h2"]))
    story.append(
        Paragraph(
            f"Population nationale recensée : <b>{pop_nat:,.0f}</b> habitants. "
            "Les préfectures du littoral concentrent l'essentiel des effectifs ; "
            "l'intérieur présente des territoires plus petits mais stratégiques pour l'équité.",
            styles["body"],
        )
    )
    top5 = pref.nlargest(5, "population_2022")[
        ["prefecture_nom", "region_nom", "population_2022", "poids_national_pct"]
    ]
    rows = [["Préfecture", "Région", "Population", "Part Togo (%)"]]
    for _, row in top5.iterrows():
        rows.append(
            [
                row["prefecture_nom"],
                row["region_nom"],
                f"{row['population_2022']:,.0f}",
                f"{row['poids_national_pct']:.2f}",
            ]
        )
    table = Table(rows, colWidths=[width * 0.28, width * 0.22, width * 0.28, width * 0.22])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TOGO_GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, TOGO_MUTED),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ]
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(table)
    story.append(PageBreak())

    # 5 - Evolution
    n_comp = len(evol[evol["comparable_decoupage"] == "oui"])
    story.append(Paragraph("4. Évolution 2010-2022", styles["h2"]))
    story.append(
        Paragraph(
            f"{n_comp} préfectures sur 39 sont comparables directement (libellés alignés). "
            "Les autres évoluent avec le découpage administratif.",
            styles["body"],
        )
    )
    top_evol = evol[evol["comparable_decoupage"] == "oui"].nlargest(5, "variation_pct")
    evol_rows = [["Préfecture", "Pop. 2010", "Pop. 2022", "Variation (%)"]]
    for _, row in top_evol.iterrows():
        evol_rows.append(
            [
                row["prefecture_nom"],
                f"{row['population_2010']:,.0f}",
                f"{row['population_2022']:,.0f}",
                f"{row['variation_pct']:.1f}",
            ]
        )
    evol_table = Table(evol_rows, colWidths=[width * 0.34, width * 0.22, width * 0.22, width * 0.22])
    evol_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TOGO_GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, TOGO_MUTED),
            ]
        )
    )
    story.append(evol_table)
    story.append(PageBreak())

    # 6 - Services
    story.append(Paragraph("5. Accès à l'électricité et agences", styles["h2"]))
    story.append(
        bullet_list(
            [
                f"Taux d'électricité min : {ineg_d.get('taux_electricite_min_prefecture', 0):.1f} %.",
                f"Taux max : {ineg_d.get('taux_electricite_max_prefecture', 0):.1f} %.",
                f"Agences CEET recensées : {int(kpi.get('nb_agences_ceet', 0))}.",
                f"Agences TdE recensées : {int(kpi.get('nb_agences_tde', 0))}.",
            ],
            styles["bullet"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("6. État civil et identité", styles["h2"]))
    story.append(
        Paragraph(
            "Suivi des naissances enregistrées sous 45 jours et production de CNI, passeports "
            "et cartes professionnelles. Série 2021 partielle sur certains documents (source silver).",
            styles["body"],
        )
    )
    story.append(PageBreak())

    # 7 - Recommandations
    story.append(Paragraph("7. Recommandations prioritaires", styles["h2"]))
    story.append(
        Paragraph(
            "Score gold combinant électricité, densité d'agences et croissance démographique.",
            styles["body"],
        )
    )
    reco_col_widths = [width * 0.07, width * 0.18, width * 0.08, width * 0.67]
    reco_rows = [
        [
            cell_para("Rang", styles["th"]),
            cell_para("Préfecture", styles["th"]),
            cell_para("Score", styles["th"]),
            cell_para("Synthèse", styles["th"]),
        ]
    ]
    for _, row in reco.head(8).iterrows():
        reco_rows.append(
            [
                cell_para(str(int(row["rang_priorite"])), styles["td_center"]),
                cell_para(row["prefecture_nom"], styles["td"]),
                cell_para(f"{row['score_priorite']:.1f}", styles["td_center"]),
                cell_para(row["recommandation"], styles["td"]),
            ]
        )
    reco_table = Table(reco_rows, colWidths=reco_col_widths, repeatRows=1)
    reco_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TOGO_GREEN),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, TOGO_MUTED),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ]
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(reco_table)
    story.append(PageBreak())

    # 8 - Conclusion
    story.append(Paragraph("8. Conclusion", styles["h2"]))
    story.append(
        bullet_list(
            [
                "Jointure territoriale 39/39 via référentiel et alias open data.",
                "Inégalités mesurables : communes, électricité, agences.",
                "Actions ciblées par préfecture dans mart_recommandations.csv.",
                "Dashboard Streamlit et pipeline reproductibles pour le pilotage public.",
            ],
            styles["bullet"],
        )
    )
    story.append(Spacer(1, 1 * cm))
    story.append(
        Paragraph(
            "Dépôt GitHub : TresorAlad/Defi-administration-territoriale-togo",
            styles["subtitle"],
        )
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    print(f"Rapport PDF genere : {OUT}")


if __name__ == "__main__":
    main()
