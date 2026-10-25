#!/usr/bin/env python3
"""Nettoyage CSV bronze -> data/silver/."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

BRONZE = Path(__file__).resolve().parent
DATA_ROOT = BRONZE.parent
SRC = BRONZE
OUT = DATA_ROOT / "silver"

NULL_MARKERS = frozenset(
    {
        "",
        "n/a",
        "n/a ",
        "na",
        "nsp",
        "nsp ",
        "néant",
        "neant",
        "n/a.",
        "null",
    }
)

APOSTROPHE_VARIANTS = (
    "\u2019",  # right single quotation
    "\u2018",
    "\u0060",
    "\u00b4",
)


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    for ch in APOSTROPHE_VARIANTS:
        text = text.replace(ch, "'")
    text = re.sub(r"\s+", " ", text.strip())
    return text


def null_if_placeholder(value: str) -> str:
    text = normalize_text(value)
    key = text.lower()
    if key in NULL_MARKERS:
        return ""
    return text


def unwrap_braced_set(value: str) -> str:
    """{A,B,C} -> A; B; C pour lisibilite en bronze."""
    text = null_if_placeholder(value)
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1]
        parts = [normalize_text(p) for p in inner.split(",") if normalize_text(p)]
        return "; ".join(parts)
    return text


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [], []
        fieldnames = list(reader.fieldnames)
        rows = [{k: (v or "") for k, v in row.items()} for row in reader]
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def clean_schema(path: Path, out_name: str, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned: list[dict[str, str]] = []
    for row in rows:
        cleaned.append(
            {
                "no": null_if_placeholder(row.get("No.", "")),
                "nom_du_champ": null_if_placeholder(row.get("Nom du champ", "")),
                "question": null_if_placeholder(row.get("Question", "")),
                "description": null_if_placeholder(row.get("Description", "")),
                "type_du_champ": null_if_placeholder(row.get("Type du champ", "")),
            }
        )
    out_fields = ["no", "nom_du_champ", "question", "description", "type_du_champ"]
    write_csv(OUT / out_name, out_fields, cleaned)
    report[out_name] = {"lignes": len(cleaned), "actions": ["trim", "colonnes snake_case"]}


def clean_agences(path: Path, out_name: str, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned: list[dict[str, str]] = []
    placeholder_count = 0
    for row in rows:
        raw_pairs = [
            ("region_nom_bdd", "region"),
            ("prefecture_nom_bdd", "prefecture"),
            ("commune_nom_bdd", "commune"),
            ("canton_nom_bdd", "canton"),
            ("nom_localite", "localite"),
            ("etab_nom", "etablissement"),
            ("etab_adresse", "adresse"),
            ("etab_jour", "jours_ouverture"),
            ("etab_creation_date", "annee_creation"),
            ("activite_statut", "statut_activite"),
            ("activite_categorie", "categorie"),
            ("toilette_type", "type_toilettes"),
        ]
        record = {
            "fid": null_if_placeholder(row.get("FID", "")),
            "region": null_if_placeholder(row.get("region_nom_bdd", "")),
            "prefecture": null_if_placeholder(row.get("prefecture_nom_bdd", "")),
            "commune": null_if_placeholder(row.get("commune_nom_bdd", "")),
            "canton": null_if_placeholder(row.get("canton_nom_bdd", "")),
            "localite": null_if_placeholder(row.get("nom_localite", "")),
            "etablissement": null_if_placeholder(row.get("etab_nom", "")),
            "adresse": null_if_placeholder(row.get("etab_adresse", "")),
            "jours_ouverture": unwrap_braced_set(row.get("etab_jour", "")),
            "annee_creation": null_if_placeholder(row.get("etab_creation_date", "")),
            "statut_activite": unwrap_braced_set(row.get("activite_statut", "")),
            "categorie": null_if_placeholder(row.get("activite_categorie", "")),
            "type_toilettes": unwrap_braced_set(row.get("toilette_type", "")),
            "geometry_wkt": null_if_placeholder(row.get("geometry", "")),
        }
        for raw_key, clean_key in raw_pairs:
            raw = normalize_text(row.get(raw_key, ""))
            if raw and record[clean_key] == "":
                placeholder_count += 1
        cleaned.append(record)
    fields = list(cleaned[0].keys()) if cleaned else []
    write_csv(OUT / out_name, fields, cleaned)
    report[out_name] = {
        "lignes": len(cleaned),
        "placeholders_vides": placeholder_count,
        "actions": [
            "trim espaces",
            "Nsp/N/a/Néant -> vide",
            "accolades {..} -> liste separee par ;",
            "colonnes renommees (lisibles)",
        ],
    }


def clean_observation_fsemhj(path: Path, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned: list[dict[str, str]] = []
    for row in rows:
        annee = null_if_placeholder(row.get("Date", ""))
        type_doc = normalize_text(row.get("type", ""))
        cleaned.append(
            {
                "indicateur": normalize_text(row.get("indicateur", "")),
                "type_document": type_doc,
                "unite": null_if_placeholder(row.get("Unit", "")),
                "annee": annee,
                "valeur": null_if_placeholder(row.get("Value", "")),
                "annee_incomplete": "oui" if annee == "2021" else "non",
            }
        )
    fields = [
        "indicateur",
        "type_document",
        "unite",
        "annee",
        "valeur",
        "annee_incomplete",
    ]
    write_csv(OUT / "observation-documents-identite.csv", fields, cleaned)
    report["observation-documents-identite.csv"] = {
        "lignes": len(cleaned),
        "actions": [
            "2021 flague annee_incomplete (Passeports seulement a la source)",
            "apostrophes normalisees",
        ],
    }


def clean_observation_kwwolwb(path: Path, report: dict) -> None:
    _, rows = read_csv_rows(path)
    key_counts: dict[tuple[str, ...], int] = defaultdict(int)
    cleaned: list[dict[str, str]] = []
    disambiguated = 0

    for index, row in enumerate(rows, start=2):
        indicateur = normalize_text(row.get("indicateur", ""))
        decoupage = normalize_text(row.get("découpage-administratif", ""))
        sexe = normalize_text(row.get("sexe", ""))
        unite = null_if_placeholder(row.get("Unit", ""))
        annee = null_if_placeholder(row.get("Date", ""))
        valeur = null_if_placeholder(row.get("Value", ""))

        base_key = (indicateur, decoupage, sexe, unite, annee)
        key_counts[base_key] += 1
        occurrence = key_counts[base_key]

        decoupage_final = decoupage
        niveau = "standard"
        if occurrence > 1:
            disambiguated += 1
            decoupage_final = f"{decoupage} (occurrence {occurrence})"
            niveau = "homonyme"

        cleaned.append(
            {
                "indicateur": indicateur,
                "decoupage_administratif": decoupage_final,
                "decoupage_source": decoupage,
                "sexe": sexe,
                "unite": unite,
                "annee": annee,
                "valeur": valeur,
                "occurrence": str(occurrence),
                "niveau_decoupage": niveau,
                "ligne_source": str(index),
            }
        )

    fields = list(cleaned[0].keys()) if cleaned else []
    write_csv(OUT / "observation-population-decoupage.csv", fields, cleaned)
    report["observation-population-decoupage.csv"] = {
        "lignes": len(cleaned),
        "doublons_desambiguisés": disambiguated,
        "actions": [
            "13 cles en double -> suffixe (occurrence N) + colonne niveau_decoupage",
            "conserve decoupage_source et ligne_source pour tracabilite",
        ],
    }


def clean_observation_puncgpd(path: Path, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned = []
    for row in rows:
        cleaned.append(
            {
                "indicateur": normalize_text(row.get("indicateur", "")),
                "prefecture": normalize_text(row.get("préfecture", "")),
                "libelle": normalize_text(row.get("libellés", "")),
                "unite": null_if_placeholder(row.get("Unit", "")),
                "annee": null_if_placeholder(row.get("Date", "")),
                "valeur": null_if_placeholder(row.get("Value", "")),
            }
        )
    fields = list(cleaned[0].keys()) if cleaned else []
    write_csv(OUT / "observation-acces-electricite.csv", fields, cleaned)
    report["observation-acces-electricite.csv"] = {
        "lignes": len(cleaned),
        "actions": ["trim", "colonnes harmonisees"],
    }


def clean_observation_sapxctg(path: Path, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned = []
    for row in rows:
        unite = null_if_placeholder(row.get("Unit", "")) or "Nombre"
        cleaned.append(
            {
                "indicateur": normalize_text(row.get("indicateurs", "")),
                "unite": unite,
                "annee": null_if_placeholder(row.get("Date", "")),
                "valeur": null_if_placeholder(row.get("Value", "")),
            }
        )
    fields = list(cleaned[0].keys()) if cleaned else []
    write_csv(OUT / "observation-population-hierarchie-2010.csv", fields, cleaned)
    report["observation-population-hierarchie-2010.csv"] = {
        "lignes": len(cleaned),
        "actions": [
            "Unit vide rempli par Nombre",
            "indicateurs -> indicateur",
        ],
    }


def clean_observation_vrsicxf(path: Path, report: dict) -> None:
    _, rows = read_csv_rows(path)
    cleaned = []
    for row in rows:
        sexe = normalize_text(row.get("sexe", ""))
        if sexe == "Tota":
            sexe = "Total"
        cleaned.append(
            {
                "indicateur": normalize_text(row.get("indicateur", "")),
                "sexe": sexe,
                "unite": null_if_placeholder(row.get("Unit", "")),
                "annee": null_if_placeholder(row.get("Date", "")),
                "valeur": null_if_placeholder(row.get("Value", "")),
            }
        )
    fields = list(cleaned[0].keys()) if cleaned else []
    write_csv(OUT / "observation-enregistrement-etat-civil.csv", fields, cleaned)
    report["observation-enregistrement-etat-civil.csv"] = {
        "lignes": len(cleaned),
        "actions": ["Tota -> Total", "espaces multiples reduits dans indicateur"],
    }


def copy_unchanged(path: Path, out_name: str, report: dict) -> None:
    _, rows = read_csv_rows(path)
    if not rows:
        return
    fields = list(rows[0].keys())
    write_csv(OUT / out_name, fields, rows)
    report[out_name] = {"lignes": len(rows), "actions": ["copie sans transformation"]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict] = {}

    clean_schema(SRC / "schema-ceet.csv", "schema-ceet.csv", report)
    clean_schema(
        SRC / "schema-togolaise-des-eaux-tde.csv",
        "schema-togolaise-des-eaux-tde.csv",
        report,
    )
    clean_agences(
        SRC / "file-agences-ceet-23-12-2024-11-06-42.csv",
        "agences-ceet.csv",
        report,
    )
    clean_agences(
        SRC / "file-agences-togolaise-des-eaux-tde-19-12-2024-17-48-23.csv",
        "agences-tde.csv",
        report,
    )
    clean_observation_fsemhj(SRC / "observationdata-fsemhj.csv", report)
    clean_observation_kwwolwb(SRC / "observationdata-kwwolwb.csv", report)
    clean_observation_puncgpd(SRC / "observationdata-puncgpd.csv", report)
    clean_observation_sapxctg(SRC / "observationdata-sapxctg.csv", report)
    clean_observation_vrsicxf(SRC / "observationdata-vrsicxf.csv", report)
    copy_unchanged(
        SRC / "adf-togo-data-pipeli_migration_analysis.csv",
        "adf-togo-data-pipeli_migration_analysis.csv",
        report,
    )

    manifest = {"source": str(SRC), "destination": str(OUT), "fichiers": report}
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
