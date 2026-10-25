#!/usr/bin/env python3
"""Genere data/ref/*.csv depuis la subdivision administrative Togo (source ouverte)."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

REF = Path(__file__).resolve().parent
SOURCE_BASE = (
    "https://raw.githubusercontent.com/gausoft/Subdivision_administrative_Togo/main/data/csv"
)


def normalize_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def slug_code(value: str, max_len: int = 24) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").upper()
    return text[:max_len]


def load_source() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    regions = pd.read_csv(f"{SOURCE_BASE}/regions.csv")
    prefectures = pd.read_csv(f"{SOURCE_BASE}/prefectures.csv")
    communes = pd.read_csv(f"{SOURCE_BASE}/communes.csv")
    return regions, prefectures, communes


def build_regions(regions: pd.DataFrame) -> pd.DataFrame:
    out = regions.rename(columns={"id": "region_id", "code": "region_code", "nom": "region_nom"})
    return out[["region_id", "region_code", "region_nom", "latitude", "longitude", "superficie"]]


def build_prefectures(regions: pd.DataFrame, prefectures: pd.DataFrame) -> pd.DataFrame:
    reg = regions.rename(columns={"id": "region_id", "code": "region_code", "nom": "region_nom"})
    pref = prefectures.rename(columns={"id": "prefecture_id", "nom": "prefecture_nom"})
    merged = pref.merge(reg[["region_id", "region_code", "region_nom"]], on="region_id", how="left")
    merged["prefecture_code"] = merged.apply(
        lambda row: f"{row['region_code']}-{slug_code(row['prefecture_nom'])}",
        axis=1,
    )
    merged["cle_normalisee"] = merged["prefecture_nom"].map(normalize_key)
    return merged[
        [
            "prefecture_id",
            "prefecture_code",
            "prefecture_nom",
            "chef_lieu",
            "region_id",
            "region_code",
            "region_nom",
            "latitude",
            "longitude",
            "cle_normalisee",
        ]
    ]


def build_communes(prefectures_out: pd.DataFrame, communes: pd.DataFrame) -> pd.DataFrame:
    pref = prefectures_out[
        ["prefecture_id", "prefecture_code", "prefecture_nom", "region_id", "region_code", "region_nom"]
    ]
    com = communes.rename(columns={"id": "commune_id", "nom": "commune_nom"})
    merged = com.merge(pref, on="prefecture_id", how="left")
    merged["commune_code"] = merged.apply(
        lambda row: f"{row['prefecture_code']}-{slug_code(row['commune_nom'])}",
        axis=1,
    )
    merged["cle_normalisee"] = merged["commune_nom"].map(normalize_key)
    return merged[
        [
            "commune_id",
            "commune_code",
            "commune_nom",
            "prefecture_id",
            "prefecture_code",
            "prefecture_nom",
            "region_id",
            "region_code",
            "region_nom",
            "latitude",
            "longitude",
            "population",
            "superficie",
            "cle_normalisee",
        ]
    ]


def build_mapping_prefectures(prefectures_out: pd.DataFrame) -> pd.DataFrame:
    """Alias pour joindre electricite (open data) et agences sur prefecture_id."""
    rows: list[dict[str, str | int]] = []

    def add(alias: str, prefecture_id: int, source: str) -> None:
        rows.append(
            {
                "alias": alias,
                "cle_normalisee": normalize_key(alias),
                "prefecture_id": prefecture_id,
                "source_jeu": source,
            }
        )

    by_key = {row["cle_normalisee"]: int(row["prefecture_id"]) for _, row in prefectures_out.iterrows()}
    by_nom = {normalize_key(row["prefecture_nom"]): int(row["prefecture_id"]) for _, row in prefectures_out.iterrows()}

    for _, row in prefectures_out.iterrows():
        pid = int(row["prefecture_id"])
        add(row["prefecture_nom"], pid, "referentiel")
        add(row["cle_normalisee"], pid, "referentiel")

    # Agences (data/silver)
    agences_aliases = {
        "AGOENYIVE": "Agoè-Nyivé",
        "AGOU": "Agou",
        "AMOU": "Amou",
        "ANIE": "Anié",
        "ASSOLI": "Assoli",
        "AVE": "Avé",
        "BASSAR": "Bassar",
        "BINAH": "Binah",
        "BLITTA": "Blitta",
        "CINKASSE": "Cinkassé",
        "DANKPEN": "Dankpen",
        "DANYI": "Danyi",
        "DOUFELGOU": "Doufelgou",
        "EST MONO": "Est-Mono",
        "EST-MONO": "Est-Mono",
        "GOLFE": "Golfe",
        "HAHO": "Haho",
        "KERAN": "Kéran",
        "KLOTO": "Kloto",
        "KOZAH": "Kozah",
        "KPENDJAL": "Kpendjal",
        "LACS": "Lacs",
        "MO": "Mô",
        "MOYEN MONO": "Moyen-Mono",
        "OGOU": "Ogou",
        "OTI": "Oti",
        "OTI SUD": "Oti-Sud",
        "OTI-SUD": "Oti-Sud",
        "SOTOUBOUA": "Sotouboua",
        "TANDJOARE": "Tandjoaré",
        "TCHAMBA": "Tchamba",
        "TCHAOUDJO": "Tchaoudjo",
        "TONE": "Tône",
        "VO": "Vo",
        "WAWA": "Wawa",
        "YOTO": "Yoto",
        "ZIO": "Zio",
    }
    for alias, canonical in agences_aliases.items():
        key = normalize_key(canonical)
        if key in by_nom:
            add(alias, by_nom[key], "agences")

    alias_path = REF / "alias_open_data.csv"
    if alias_path.exists():
        alias_df = pd.read_csv(alias_path)
        for _, row in alias_df.iterrows():
            add(row["cle_open_data"], int(row["prefecture_id"]), str(row["jeu"]))

    # Electricite (libelles agreges open data)
    elec_map: list[tuple[str, list[str]]] = [
        ("LOME", ["Golfe"]),
        ("LOME COMMUNE + GOLFE", ["Golfe"]),
        ("HAHO + MOYEN MONO", ["Haho", "Moyen-Mono"]),
        ("LACS + BAS-MONO", ["Lacs", "Bas-Mono"]),
        ("OGOU + ANIE", ["Ogou", "Anié"]),
        ("OTI + OTI SUD", ["Oti", "Oti-Sud"]),
        ("KPENDJAL + KPENDJAL OUEST", ["Kpendjal", "Kpendjal-Ouest"]),
        ("SOTOUBOUA + PLAINE DE MO", ["Sotouboua", "Mô"]),
        ("KPELE", ["Kpélé"]),
        ("AKEBOU", ["Akébou"]),
    ]
    for alias, pref_names in elec_map:
        for name in pref_names:
            key = normalize_key(name)
            if key in by_nom:
                add(alias, by_nom[key], "electricite")

    # Regions entieres (lignes agregats electricite) : pas de prefecture_id unique
    for alias in [
        "ENSEMBLE DU PAYS",
        "REGION MARITIME",
        "REGION DES PLATEAUX",
        "REGION CENTRALE",
        "REGION DE LA KARA",
        "REGION DES SAVANES",
    ]:
        rows.append(
            {
                "alias": alias,
                "cle_normalisee": normalize_key(alias),
                "prefecture_id": "",
                "source_jeu": "electricite_agregat",
            }
        )

    mapping = pd.DataFrame(rows).drop_duplicates(subset=["alias", "prefecture_id", "source_jeu"])
    return mapping


def main() -> None:
    regions, prefectures, communes = load_source()
    regions_out = build_regions(regions)
    prefectures_out = build_prefectures(regions, prefectures)
    communes_out = build_communes(prefectures_out, communes)
    mapping_out = build_mapping_prefectures(prefectures_out)

    regions_out.to_csv(REF / "regions.csv", index=False)
    prefectures_out.to_csv(REF / "prefectures.csv", index=False)
    communes_out.to_csv(REF / "communes.csv", index=False)
    mapping_out.to_csv(REF / "mapping_libelles.csv", index=False)

    meta = {
        "prefectures": len(prefectures_out),
        "communes": len(communes_out),
        "regions": len(regions_out),
        "mapping_lignes": len(mapping_out),
        "source": SOURCE_BASE,
        "note": "117 communes / 39 prefectures / 5 regions (communalisation 2019)",
    }
    (REF / "manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(meta)


if __name__ == "__main__":
    main()
