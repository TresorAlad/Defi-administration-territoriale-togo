"""Charte graphique Togo : blanc dominant, accents drapeau (vert, jaune, rouge)."""

from __future__ import annotations

import html
import plotly.graph_objects as go
import streamlit as st

TOGO_GREEN = "#006A4E"
TOGO_YELLOW = "#FFCE00"
TOGO_RED = "#D21034"
TOGO_WHITE = "#FFFFFF"
TOGO_INK = "#1F2937"
TOGO_MUTED = "#6B7280"
TOGO_BORDER = "#E5E7EB"

TOGO_SEQUENCE = [TOGO_GREEN, TOGO_YELLOW, TOGO_RED, "#00875A", "#C4A000", "#B91C1C"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=TOGO_WHITE,
    plot_bgcolor=TOGO_WHITE,
    font=dict(color=TOGO_INK, family="Inter, system-ui, sans-serif"),
    colorway=TOGO_SEQUENCE,
    margin=dict(l=24, r=24, t=48, b=24),
    xaxis=dict(gridcolor="#F3F4F6", linecolor=TOGO_BORDER, zerolinecolor=TOGO_BORDER),
    yaxis=dict(gridcolor="#F3F4F6", linecolor=TOGO_BORDER, zerolinecolor=TOGO_BORDER),
)


def apply_togo_theme() -> None:
    st.markdown(
        f"""
<style>
    .stApp {{
        background-color: {TOGO_WHITE};
    }}
    [data-testid="stSidebar"] {{
        background-color: {TOGO_WHITE};
        border-right: 3px solid {TOGO_GREEN};
    }}
    [data-testid="stMetric"] {{
        background: {TOGO_WHITE};
        border: 1px solid {TOGO_BORDER};
        border-left: 4px solid {TOGO_GREEN};
        padding: 0.75rem 1rem;
        border-radius: 8px;
    }}
    [data-testid="stMetric"]:nth-of-type(3n+2) {{
        border-left-color: {TOGO_YELLOW};
    }}
    [data-testid="stMetric"]:nth-of-type(3n) {{
        border-left-color: {TOGO_RED};
    }}
    div[data-testid="stExpander"] {{
        background: {TOGO_WHITE};
        border: 1px solid {TOGO_BORDER};
        border-radius: 8px;
    }}
    .togo-hero {{
        background: {TOGO_WHITE};
        border: 1px solid {TOGO_BORDER};
        border-radius: 12px;
        padding: 0.25rem 0 1rem 0;
        margin-bottom: 1rem;
    }}
    .togo-stripe {{
        height: 6px;
        border-radius: 12px 12px 0 0;
        background: linear-gradient(
            90deg,
            {TOGO_GREEN} 0%,
            {TOGO_GREEN} 33.33%,
            {TOGO_YELLOW} 33.33%,
            {TOGO_YELLOW} 66.66%,
            {TOGO_RED} 66.66%,
            {TOGO_RED} 100%
        );
        margin-bottom: 1rem;
    }}
    .togo-hero h1 {{
        color: {TOGO_INK};
        padding: 0 1.25rem;
        margin: 0;
        font-weight: 700;
    }}
    .togo-hero p {{
        color: {TOGO_MUTED};
        padding: 0 1.25rem;
        margin: 0.35rem 0 0 0;
        line-height: 1.55;
    }}
    .togo-section {{
        background: {TOGO_WHITE};
        border: 1px solid {TOGO_BORDER};
        border-left: 4px solid {TOGO_GREEN};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0 1.25rem 0;
    }}
    .togo-section h3 {{
        color: {TOGO_INK};
        font-size: 1.05rem;
        margin: 0 0 0.45rem 0;
        font-weight: 600;
    }}
    .togo-section p {{
        color: {TOGO_MUTED};
        margin: 0;
        line-height: 1.6;
        font-size: 0.96rem;
    }}
    .togo-lead {{
        color: {TOGO_MUTED};
        font-size: 1rem;
        line-height: 1.65;
        margin: 0 0 1.25rem 0;
    }}
    [data-testid="stAlert"] {{
        background-color: {TOGO_WHITE};
        border: 1px solid {TOGO_GREEN};
        color: {TOGO_INK};
    }}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str = "") -> None:
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
<div class="togo-hero">
  <div class="togo-stripe"></div>
  <h1>{html.escape(title)}</h1>
  {sub}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_lead(text: str) -> None:
    st.markdown(f'<p class="togo-lead">{html.escape(text)}</p>', unsafe_allow_html=True)


def render_section(title: str, body: str) -> None:
    st.markdown(
        f"""
<div class="togo-section">
  <h3>{html.escape(title)}</h3>
  <p>{html.escape(body)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def px_defaults() -> dict:
    return {"color_discrete_sequence": TOGO_SEQUENCE}
