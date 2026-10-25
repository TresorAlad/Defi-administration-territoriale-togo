"""Chargement de la couche gold pour Streamlit."""

import bootstrap  # noqa: F401

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD = PROJECT_ROOT / "data" / "gold"


@st.cache_data
def load_gold(name: str) -> pd.DataFrame:
    path = GOLD / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def require_gold() -> bool:
    if not (GOLD / "mart_profil_prefecture.csv").exists():
        st.error(
            "Couche gold absente. Exécuter :\n\n"
            "`python3 data/bronze/clean_data.py`\n\n"
            "`python3 -m pipeline.gold.build`"
        )
        return False
    return True
