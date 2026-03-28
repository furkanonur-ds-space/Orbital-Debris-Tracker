"""
visualizer.py
-------------
Builds an interactive Plotly 3D orthographic globe figure from a DataFrame
produced by data_fetcher.build_dataframe / load_groups.

Usage
-----
    from core.visualizer import build_globe_figure, save_html
    fig = build_globe_figure(df)
    fig.show()                    # open in browser
    save_html(fig, "output.html") # export static file
"""

import pandas as pd
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GLOBE_LAYOUT = dict(
    paper_bgcolor="#0a0a1a",
    plot_bgcolor="#0a0a1a",
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(
        bgcolor="rgba(10,10,40,0.8)",
        bordercolor="#334",
        borderwidth=1,
        font=dict(color="#ccd", size=12),
        itemsizing="constant",
    ),
)

_GEO_LAYOUT = dict(
    showframe=False,
    showcoastlines=True,
    coastlinecolor="#334466",
    coastlinewidth=0.8,
    showland=True,
    landcolor="#1a1a2e",
    showocean=True,
    oceancolor="#0d1117",
    showlakes=True,
    lakecolor="#0d1117",
    showcountries=True,
    countrycolor="#223344",
    countrywidth=0.5,
    bgcolor="#0a0a1a",
    projection_type="orthographic",
    projection_rotation=dict(lon=0, lat=20, roll=0),
)


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_globe_figure(df: pd.DataFrame, title: str = "🛰️ Orbital Debris & Satellite Tracker") -> go.Figure:
    """
    Build an interactive Plotly orthographic globe figure.

    Each unique `group` in the DataFrame becomes a separate trace,
    enabling legend-based show/hide per category.

    Parameters
    ----------
    df    : pd.DataFrame
        Must contain columns: name, lat, lon, alt_km, group, type_label, color.
    title : str
        Figure title shown at the top.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    if df.empty:
        return go.Figure(layout=go.Layout(title="No data available", **_GLOBE_LAYOUT))

    fig = go.Figure()

    for group_key, group_df in df.groupby("group"):
        color = group_df["color"].iloc[0]
        label = group_df["type_label"].iloc[0]
        count = len(group_df)

        hover_text = (
            "<b>%{text}</b><br>"
            "Lat: %{lat:.2f}°<br>"
            "Lon: %{lon:.2f}°<br>"
            "Alt: %{customdata[0]:.1f} km<br>"
            f"Type: {label}"
            "<extra></extra>"
        )

        fig.add_trace(
            go.Scattergeo(
                lat=group_df["lat"],
                lon=group_df["lon"],
                text=group_df["name"],
                customdata=group_df[["alt_km"]].values,
                mode="markers",
                name=f"{label} ({count})",
                marker=dict(
                    size=_marker_size(group_key),
                    color=color,
                    opacity=0.85,
                    line=dict(width=0),
                    symbol="circle",
                ),
                hovertemplate=hover_text,
            )
        )

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            font=dict(color="#e0e8ff", size=18, family="monospace"),
        ),
        geo=_GEO_LAYOUT,
        **_GLOBE_LAYOUT,
    )

    return fig


def build_risk_globe_figure(
    df: pd.DataFrame,
    risk_df: pd.DataFrame,
    title: str = "⚠️ Conjunction Assessment — High Risk Objects",
) -> go.Figure:
    """
    Same as build_globe_figure but overlays a red 'High Risk' trace
    for objects flagged by the risk engine.

    Parameters
    ----------
    df      : pd.DataFrame — full satellite DataFrame
    risk_df : pd.DataFrame — must contain 'name' column of at-risk objects
    """
    fig = build_globe_figure(df, title=title)

    if risk_df.empty:
        return fig

    # Build a set of all at-risk names
    risk_names = set(risk_df["name_a"]).union(set(risk_df["name_b"]))
    high_risk_df = df[df["name"].isin(risk_names)]

    if high_risk_df.empty:
        return fig

    fig.add_trace(
        go.Scattergeo(
            lat=high_risk_df["lat"],
            lon=high_risk_df["lon"],
            text=high_risk_df["name"],
            customdata=high_risk_df[["alt_km"]].values,
            mode="markers",
            name=f"⚠️ HIGH RISK ({len(high_risk_df)})",
            marker=dict(
                size=10,
                color="#FF0000",
                opacity=1.0,
                line=dict(width=1.5, color="#FFAAAA"),
                symbol="circle",
            ),
            hovertemplate=(
                "<b>⚠️ HIGH RISK: %{text}</b><br>"
                "Lat: %{lat:.2f}°  Lon: %{lon:.2f}°<br>"
                "Alt: %{customdata[0]:.1f} km"
                "<extra></extra>"
            ),
        )
    )
    return fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _marker_size(group_key: str) -> int:
    """Return marker size based on object category."""
    if "station" in group_key:
        return 9
    if "debris" in group_key:
        return 3
    return 4  # active satellites


def save_html(fig: go.Figure, path: str = "output.html") -> None:
    """Export figure to a standalone HTML file."""
    fig.write_html(path, include_plotlyjs="cdn")
    print(f"Globe saved → {path}")
