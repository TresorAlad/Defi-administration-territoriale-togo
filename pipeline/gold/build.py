#!/usr/bin/env python3
"""Construit la couche gold (pret pour dashboard) depuis silver + ref."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pipeline.gold.normalize import normalize_key

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER = PROJECT_ROOT / "data" / "silver"
GOLD = PROJECT_ROOT / "data" / "gold"
REF = PROJECT_ROOT / "data" / "ref"


def load_silver(name: str) -> pd.DataFrame:
    return pd.read_csv(SILVER / name)


def load_ref(name: str) -> pd.DataFrame:
    return pd.read_csv(REF / name)


def load_aliases(jeu: str) -> dict[str, int]:
    path = REF / "alias_open_data.csv"
    if not path.exists():
        return {}
    frame = pd.read_csv(path)
    frame = frame[frame["jeu"] == jeu]
    return {str(row["cle_open_data"]): int(row["prefecture_id"]) for _, row in frame.iterrows()}


def build_dim_territoire() -> pd.DataFrame:
    regions = load_ref("regions.csv")
    prefectures = load_ref("prefectures.csv")
    communes = load_ref("communes.csv")

    rows: list[dict] = []
    for _, row in regions.iterrows():
        rows.append(
            {
                "territoire_id": f"R{int(row['region_id'])}",
                "code": row["region_code"],
                "libelle": row["region_nom"],
                "niveau": "region",
                "parent_territoire_id": "",
                "region_id": int(row["region_id"]),
                "prefecture_id": "",
                "commune_id": "",
                "cle_normalisee": normalize_key(row["region_nom"]),
            }
        )
    for _, row in prefectures.iterrows():
        rows.append(
            {
                "territoire_id": f"P{int(row['prefecture_id'])}",
                "code": row["prefecture_code"],
                "libelle": row["prefecture_nom"],
                "niveau": "prefecture",
                "parent_territoire_id": f"R{int(row['region_id'])}",
                "region_id": int(row["region_id"]),
                "prefecture_id": int(row["prefecture_id"]),
                "commune_id": "",
                "cle_normalisee": row["cle_normalisee"],
            }
        )
    for _, row in communes.iterrows():
        rows.append(
            {
                "territoire_id": f"C{int(row['commune_id'])}",
                "code": row["commune_code"],
                "libelle": row["commune_nom"],
                "niveau": "commune",
                "parent_territoire_id": f"P{int(row['prefecture_id'])}",
                "region_id": int(row["region_id"]),
                "prefecture_id": int(row["prefecture_id"]),
                "commune_id": int(row["commune_id"]),
                "cle_normalisee": row["cle_normalisee"],
            }
        )
    return pd.DataFrame(rows)


def build_fact_agence() -> pd.DataFrame:
    ceet = load_silver("agences-ceet.csv")
    ceet["operateur"] = "CEET"
    tde = load_silver("agences-tde.csv")
    tde["operateur"] = "TdE"
    frame = pd.concat([ceet, tde], ignore_index=True)
    prefs = load_ref("prefectures.csv")
    pref_by_cle = prefs.set_index("cle_normalisee")["prefecture_id"].to_dict()
    frame["cle_prefecture"] = frame["prefecture"].map(normalize_key)
    # Agences : Agoe-Nyive vs referentiel AGOUE NYIVE
    alias_agences = {"AGOENYIVE": "AGOUE NYIVE", "AGOÈ NYIVÉ": "AGOUE NYIVE"}
    frame["cle_prefecture"] = frame["cle_prefecture"].replace(alias_agences)
    frame["prefecture_id"] = frame["cle_prefecture"].map(pref_by_cle)
    return frame


def build_fact_electricite() -> pd.DataFrame:
    raw = load_silver("observation-acces-electricite.csv")
    raw["valeur"] = pd.to_numeric(raw["valeur"], errors="coerce")
    mapping = load_ref("mapping_libelles.csv")
    mapping = mapping[mapping["prefecture_id"].notna() & (mapping["prefecture_id"] != "")]
    mapping["prefecture_id"] = mapping["prefecture_id"].astype(int)
    map_elec = mapping[mapping["source_jeu"] == "electricite"][
        ["alias", "prefecture_id"]
    ].drop_duplicates()
    raw["cle_prefecture"] = raw["prefecture"].map(normalize_key)
    merged = raw.merge(
        map_elec,
        left_on="prefecture",
        right_on="alias",
        how="left",
    )
    prefs = load_ref("prefectures.csv")
    pref_by_cle = prefs.set_index("cle_normalisee")["prefecture_id"].to_dict()
    direct = merged["prefecture"].map(normalize_key).map(pref_by_cle)
    merged["prefecture_id"] = merged["prefecture_id"].fillna(direct)
    alias_elec = load_aliases("electricite")
    merged["prefecture_id"] = merged["prefecture_id"].fillna(
        merged["prefecture"].map(normalize_key).map(alias_elec)
    )
    return merged


def build_fact_population_2022() -> pd.DataFrame:
    raw = load_silver("observation-population-decoupage.csv")
    raw = raw[raw["sexe"] == "Total"].copy()
    raw["valeur"] = pd.to_numeric(raw["valeur"], errors="coerce")
    raw["annee"] = pd.to_numeric(raw["annee"], errors="coerce").astype("Int64")
    raw["occurrence"] = pd.to_numeric(raw["occurrence"], errors="coerce").fillna(1).astype(int)
    raw["cle_decoupage"] = raw["decoupage_source"].map(normalize_key)
    dim = build_dim_territoire()
    cle_to_territoire = dim.set_index("cle_normalisee")[["territoire_id", "niveau"]].to_dict("index")
    raw["territoire_id"] = raw["cle_decoupage"].map(lambda c: cle_to_territoire.get(c, {}).get("territoire_id", ""))
    raw["niveau_ref"] = raw["cle_decoupage"].map(lambda c: cle_to_territoire.get(c, {}).get("niveau", ""))
    return raw


def population_prefecture_level(pop: pd.DataFrame) -> pd.DataFrame:
    """Population 2022 au niveau prefecture (1ere occurrence + alias open data)."""
    prefs = load_ref("prefectures.csv")
    alias_pop = load_aliases("population")
    records: list[dict] = []

    pop_occ1 = pop[pop["occurrence"] == 1]
    for _, pref in prefs.iterrows():
        cle_ref = pref["cle_normalisee"]
        candidates = [cle_ref]
        for open_cle, pid in alias_pop.items():
            if int(pid) == int(pref["prefecture_id"]):
                candidates.append(open_cle)
        value = pd.NA
        for candidate in candidates:
            match = pop_occ1.loc[pop_occ1["cle_decoupage"] == candidate, "valeur"]
            if not match.empty:
                value = match.iloc[0]
                break
        if pd.notna(value):
            records.append({"cle_normalisee": cle_ref, "population_2022": value})

    return pd.DataFrame(records)


def population_commune_level(pop: pd.DataFrame) -> pd.DataFrame:
    communes = load_ref("communes.csv")
    keys = set(communes["cle_normalisee"])
    subset = pop[(pop["occurrence"] == 1) & (pop["cle_decoupage"].isin(keys))].copy()
    subset = subset.rename(columns={"valeur": "population_2022", "cle_decoupage": "cle_normalisee"})
    return subset[["cle_normalisee", "population_2022"]].drop_duplicates(subset=["cle_normalisee"])


def latest_electricite_taux(fact_elec: pd.DataFrame) -> pd.DataFrame:
    taux = fact_elec[fact_elec["libelle"].str.contains("Taux", na=False)].copy()
    taux = taux[taux["prefecture_id"].notna()]
    taux["annee"] = pd.to_numeric(taux["annee"], errors="coerce")
    taux = taux.sort_values("annee")
    latest = taux.groupby("prefecture_id", as_index=False).tail(1)
    return latest.rename(columns={"valeur": "taux_acces_electricite_pct", "annee": "annee_electricite"})[
        ["prefecture_id", "annee_electricite", "taux_acces_electricite_pct"]
    ]


def build_mart_profil_prefecture(
    pop: pd.DataFrame,
    agences: pd.DataFrame,
    fact_elec: pd.DataFrame,
) -> pd.DataFrame:
    prefs = load_ref("prefectures.csv")
    pop_pref = population_prefecture_level(pop)
    mart = prefs.merge(pop_pref, on="cle_normalisee", how="left")

    pop_nationale = pop.loc[pop["cle_decoupage"] == "TOGO", "valeur"].max()
    mart["poids_national_pct"] = (mart["population_2022"] / pop_nationale * 100).round(2)

    elec = latest_electricite_taux(fact_elec)
    mart = mart.merge(elec, on="prefecture_id", how="left")

    ag_count = (
        agences.groupby(["prefecture_id", "operateur"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("CEET", "TdE"):
        if col not in ag_count.columns:
            ag_count[col] = 0
    ag_count = ag_count.rename(columns={"CEET": "nb_agences_ceet", "TdE": "nb_agences_tde"})
    mart = mart.merge(ag_count, on="prefecture_id", how="left")
    mart["nb_agences_ceet"] = mart["nb_agences_ceet"].fillna(0).astype(int)
    mart["nb_agences_tde"] = mart["nb_agences_tde"].fillna(0).astype(int)
    mart["nb_agences_total"] = mart["nb_agences_ceet"] + mart["nb_agences_tde"]
    mart["habitants_par_agence"] = mart.apply(
        lambda row: row["population_2022"] / row["nb_agences_total"]
        if row["nb_agences_total"] > 0 and pd.notna(row["population_2022"])
        else pd.NA,
        axis=1,
    )

    mart["rang_population"] = mart["population_2022"].rank(ascending=False, method="min").astype("Int64")
    mart = mart.sort_values("population_2022", ascending=False)
    return mart


def build_mart_profil_commune(pop: pd.DataFrame) -> pd.DataFrame:
    communes = load_ref("communes.csv")
    pop_com = population_commune_level(pop)
    mart = communes.merge(pop_com, on="cle_normalisee", how="left")
    pop_nationale = pop.loc[pop["cle_decoupage"] == "TOGO", "valeur"].max()
    mart["poids_national_pct"] = (mart["population_2022"] / pop_nationale * 100).round(3)
    pref_pop = (
        mart.groupby("prefecture_id")["population_2022"]
        .transform("sum")
    )
    mart["poids_prefecture_pct"] = (mart["population_2022"] / pref_pop * 100).round(2)
    mart["rang_population_commune"] = mart["population_2022"].rank(ascending=False, method="min").astype("Int64")
    return mart.sort_values("population_2022", ascending=False)


def build_mart_inegalites(mart_pref: pd.DataFrame, mart_com: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    pop_com = mart_com["population_2022"].dropna()
    ratio_communes = pop_com.max() / pop_com.min() if pop_com.min() > 0 else pd.NA

    pref = mart_pref.dropna(subset=["population_2022"])
    golfe = pref.loc[pref["cle_normalisee"] == "GOLFE", "population_2022"].sum()
    agoe = pref.loc[pref["cle_normalisee"] == "AGOUE NYIVE", "population_2022"].sum()
    grand_lome = golfe + agoe
    pop_nationale = pop.loc[pop["cle_decoupage"] == "TOGO", "valeur"].max()

    maritime_cle = normalize_key("Maritime")
    pop_maritime = pop.loc[
        (pop["cle_decoupage"] == maritime_cle) & (pop["occurrence"] == 1), "valeur"
    ]
    part_maritime = float(pop_maritime.iloc[0]) / pop_nationale * 100 if len(pop_maritime) else pd.NA

    rows = [
        {"indicateur": "ratio_pop_max_min_commune", "valeur": round(ratio_communes, 1), "unite": "ratio"},
        {
            "indicateur": "part_grand_lome_golfe_agoe_pct",
            "valeur": round(grand_lome / pop_nationale * 100, 2),
            "unite": "%",
        },
        {"indicateur": "part_region_maritime_pct", "valeur": round(part_maritime, 2), "unite": "%"},
        {
            "indicateur": "prefecture_pop_min",
            "valeur": pref["population_2022"].min(),
            "unite": "habitants",
        },
        {
            "indicateur": "prefecture_pop_max",
            "valeur": pref["population_2022"].max(),
            "unite": "habitants",
        },
        {
            "indicateur": "taux_electricite_min_prefecture",
            "valeur": pref["taux_acces_electricite_pct"].min(),
            "unite": "%",
        },
        {
            "indicateur": "taux_electricite_max_prefecture",
            "valeur": pref["taux_acces_electricite_pct"].max(),
            "unite": "%",
        },
    ]
    return pd.DataFrame(rows)


def build_mart_evolution_2010_2022(mart_pref: pd.DataFrame, pop_2010_raw: pd.DataFrame) -> pd.DataFrame:
    pop_2010 = pop_2010_raw.copy()
    pop_2010["valeur"] = pd.to_numeric(pop_2010["valeur"], errors="coerce")
    pop_2010["cle"] = pop_2010["indicateur"].map(normalize_key)
    pop_2010_by_cle = pop_2010.drop_duplicates(subset=["cle"]).set_index("cle")["valeur"]

    alias_2010 = {
        "AGOUE NYIVE": "AGOE NYIVE",
        "TANDJOUARE": "TANDJOARE",
        "AVE": "TOTOAL AVE",
    }

    rows: list[dict] = []
    for _, pref in mart_pref.iterrows():
        cle = pref["cle_normalisee"]
        pop_2010_val = pop_2010_by_cle.get(cle, pd.NA)
        if pd.isna(pop_2010_val) and cle in alias_2010:
            pop_2010_val = pop_2010_by_cle.get(alias_2010[cle], pd.NA)
        pop_2022_val = pref["population_2022"]
        comparable = pd.notna(pop_2010_val) and pd.notna(pop_2022_val)
        variation = pd.NA
        if comparable and pop_2010_val > 0:
            variation = round((pop_2022_val - pop_2010_val) / pop_2010_val * 100, 2)
        rows.append(
            {
                "prefecture_id": pref["prefecture_id"],
                "prefecture_nom": pref["prefecture_nom"],
                "region_nom": pref["region_nom"],
                "population_2010": pop_2010_val,
                "population_2022": pop_2022_val,
                "variation_pct": variation,
                "comparable_decoupage": "oui" if comparable else "non",
                "note_methodo": ""
                if comparable
                else "Pas de libelle 2010 aligne (decoupage ou nom RGPH different)",
            }
        )
    return pd.DataFrame(rows)


def build_mart_recommandations(mart_pref: pd.DataFrame, mart_evol: pd.DataFrame) -> pd.DataFrame:
    frame = mart_pref.merge(
        mart_evol[["prefecture_id", "variation_pct", "comparable_decoupage"]],
        on="prefecture_id",
        how="left",
    )
    med_elec = frame["taux_acces_electricite_pct"].median()
    med_hpa = frame["habitants_par_agence"].median()

    actions: list[str] = []
    scores: list[float] = []
    for _, row in frame.iterrows():
        score = 0.0
        reco_parts: list[str] = []

        elec = row["taux_acces_electricite_pct"]
        if pd.isna(elec) or elec < med_elec:
            gap = med_elec - (elec if pd.notna(elec) else 0)
            score += min(40, gap * 0.8)
            reco_parts.append(
                "Renforcer l'acces a l'electricite (extension reseau BT, subventions branchements)."
            )

        agences = int(row["nb_agences_total"])
        pop = row["population_2022"]
        if agences == 0 and pd.notna(pop) and pop > 80000:
            score += 35
            reco_parts.append(
                "Ouvrir au moins une agence CEET ou TdE (forte population, zero point de contact)."
            )
        elif pd.notna(row["habitants_par_agence"]) and row["habitants_par_agence"] > max(med_hpa * 1.5, 150000):
            score += 25
            reco_parts.append(
                "Densifier les agences de services publics (ratio habitants/agence au-dessus du median national)."
            )

        if row.get("comparable_decoupage") == "oui" and pd.notna(row.get("variation_pct")):
            if row["variation_pct"] > 25 and (pd.isna(elec) or elec < 40):
                score += 15
                reco_parts.append(
                    "Anticiper la demande : croissance demographique rapide 2010-2022 et acces encore faible."
                )

        if not reco_parts:
            reco_parts.append("Maintenir le niveau de service et partager les bonnes pratiques avec les territoires en retard.")

        scores.append(round(score, 1))
        actions.append(" ".join(reco_parts))

    frame["score_priorite"] = scores
    frame["rang_priorite"] = frame["score_priorite"].rank(ascending=False, method="min").astype(int)
    frame["recommandation"] = actions
    cols = [
        "rang_priorite",
        "score_priorite",
        "prefecture_nom",
        "region_nom",
        "population_2022",
        "taux_acces_electricite_pct",
        "nb_agences_ceet",
        "nb_agences_tde",
        "habitants_par_agence",
        "variation_pct",
        "recommandation",
    ]
    return frame.sort_values("score_priorite", ascending=False)[cols]


def build_mart_synthese_nationale(pop: pd.DataFrame, agences: pd.DataFrame, mart_pref: pd.DataFrame) -> pd.DataFrame:
    pop_nationale = pop.loc[pop["cle_decoupage"] == "TOGO", "valeur"].max()
    rows = [
        {"indicateur": "population_nationale_2022", "valeur": pop_nationale, "unite": "habitants"},
        {"indicateur": "nb_prefectures", "valeur": len(mart_pref), "unite": "nombre"},
        {
            "indicateur": "nb_prefectures_avec_population",
            "valeur": mart_pref["population_2022"].notna().sum(),
            "unite": "nombre",
        },
        {"indicateur": "nb_agences_ceet", "valeur": len(agences[agences["operateur"] == "CEET"]), "unite": "nombre"},
        {"indicateur": "nb_agences_tde", "valeur": len(agences[agences["operateur"] == "TdE"]), "unite": "nombre"},
    ]
    return pd.DataFrame(rows)


def main() -> None:
    GOLD.mkdir(parents=True, exist_ok=True)

    dim_territoire = build_dim_territoire()
    agences = build_fact_agence()
    fact_elec = build_fact_electricite()
    pop_2022 = build_fact_population_2022()
    etat_civil = load_silver("observation-enregistrement-etat-civil.csv")
    docs_identite = load_silver("observation-documents-identite.csv")
    pop_2010 = load_silver("observation-population-hierarchie-2010.csv")

    mart_pref = build_mart_profil_prefecture(pop_2022, agences, fact_elec)
    mart_com = build_mart_profil_commune(pop_2022)
    mart_inegalites = build_mart_inegalites(mart_pref, mart_com, pop_2022)
    mart_evol = build_mart_evolution_2010_2022(mart_pref, pop_2010)
    mart_reco = build_mart_recommandations(mart_pref, mart_evol)
    synthese = build_mart_synthese_nationale(pop_2022, agences, mart_pref)

    outputs: dict[str, pd.DataFrame] = {
        "dim_territoire.csv": dim_territoire,
        "fact_agence.csv": agences,
        "fact_electricite.csv": fact_elec,
        "fact_population_2022.csv": pop_2022,
        "fact_population_2010_brut.csv": pop_2010,
        "fact_etat_civil.csv": etat_civil,
        "fact_documents_identite.csv": docs_identite,
        "mart_profil_prefecture.csv": mart_pref,
        "mart_profil_commune.csv": mart_com,
        "mart_inegalites.csv": mart_inegalites,
        "mart_evolution_2010_2022.csv": mart_evol,
        "mart_recommandations.csv": mart_reco,
        "mart_synthese_nationale.csv": synthese,
    }

    stats: dict[str, dict] = {}
    for filename, frame in outputs.items():
        frame.to_csv(GOLD / filename, index=False)
        stats[filename] = {"lignes": len(frame), "colonnes": len(frame.columns)}

    manifest = {
        "source_silver": str(SILVER),
        "source_ref": str(REF),
        "destination": str(GOLD),
        "statut": "pret_dashboard",
        "fichiers": stats,
    }
    (GOLD / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
