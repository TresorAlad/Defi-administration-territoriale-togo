"""Filtres territoriaux partages (Streamlit)."""

from __future__ import annotations

import bootstrap  # noqa: F401

import pandas as pd
import streamlit as st


def select_region(
    mart: pd.DataFrame,
    *,
    label: str = "Filtrer par région",
    key: str = "region_filter",
) -> tuple[str, pd.DataFrame]:
    regions = ["Toutes"] + sorted(mart["region_nom"].dropna().unique().tolist())
    choice = st.selectbox(label, regions, key=key)
    if choice == "Toutes":
        return choice, mart
    return choice, mart[mart["region_nom"] == choice].copy()
