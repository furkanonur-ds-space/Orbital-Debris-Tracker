"""
app.py
------
Orbital Debris & Satellite Tracker — Streamlit Web Application

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from skyfield.api import load

from core.data_fetcher import load_groups, GROUP_LABELS
from core.visualizer import build_globe_figure, build_risk_globe_figure
from core.risk_engine import compute_distances, risk_summary

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Orbital Debris & Satellite Tracker",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS  — dark space aesthetic
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global dark background */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #070714;
        color: #c8d8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #0d0d22;
        border-right: 1px solid #1a1a40;
    }
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f0f2e 0%, #1a1a40 100%);
        border: 1px solid #2a2a60;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] { color: #7ec8e3; font-size: 1.6rem; }
    [data-testid="stMetricLabel"] { color: #8899bb; font-size: 0.8rem; }
    /* Headings */
    h1, h2, h3 { color: #a8c8ff; }
    /* Dividers */
    hr { border-color: #1a1a40; }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #1a3a6e, #0d2040);
        color: #a8d8ff;
        border: 1px solid #2a5090;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #2a5090, #1a3a6e);
        border-color: #4a80c0;
    }
    /* Checkbox text */
    .stCheckbox label { color: #aabbd0 !important; }

    /* Warning banner */
    .risk-banner {
        background: linear-gradient(90deg, #4a0000, #2a0000);
        border: 1px solid #880000;
        border-radius: 8px;
        padding: 10px 16px;
        color: #ffaaaa;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛰️ Orbital Tracker")
    st.markdown("**Data Source:** CelesTrak / NORAD")
    st.divider()

    st.markdown("### 📡 Data Groups")
    sel_stations   = st.checkbox("🟠 Space Stations",             value=True)
    sel_active     = st.checkbox("🔵 Active Satellites",          value=False)
    sel_cosmos1408 = st.checkbox("🔴 Debris — Cosmos 1408",       value=True)
    sel_fengyun    = st.checkbox("🔴 Debris — Fengyun 1C",        value=True)
    sel_iridium    = st.checkbox("🔴 Debris — Iridium 33",        value=False)
    sel_cosmos2251 = st.checkbox("🔴 Debris — Cosmos 2251",       value=False)

    st.divider()
    st.markdown("### ⚠️ Risk Analysis")
    run_risk   = st.checkbox("Enable Conjunction Assessment", value=False)
    threshold  = st.slider("Threshold (km)", min_value=10, max_value=500, value=100, step=10)

    st.divider()
    refresh = st.button("🔄 Refresh Data", use_container_width=True)

# ---------------------------------------------------------------------------
# Build selected group list
# ---------------------------------------------------------------------------
GROUP_MAP = {
    "stations":           sel_stations,
    "active":             sel_active,
    "cosmos-1408-debris": sel_cosmos1408,
    "fengyun-1c-debris":  sel_fengyun,
    "iridium-33-debris":  sel_iridium,
    "cosmos-2251-debris": sel_cosmos2251,
}
selected_groups = [g for g, active in GROUP_MAP.items() if active]

# ---------------------------------------------------------------------------
# Data loading  (cached for 5 minutes, busted by refresh button)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(groups: tuple[str, ...]) -> pd.DataFrame:
    ts = load.timescale()
    return load_groups(list(groups), ts)


# force cache bust on refresh
if "cache_key" not in st.session_state:
    st.session_state.cache_key = 0
if refresh:
    st.session_state.cache_key += 1
    st.cache_data.clear()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#7ec8e3; letter-spacing:2px;'>"
    "🌍 Orbital Debris &amp; Satellite Tracker"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#667799; font-size:0.9rem;'>"
    "Real-time LEO object tracking using NASA/CelesTrak TLE data &amp; SGP4 propagation"
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
if not selected_groups:
    st.warning("⚠️ Please select at least one data group from the sidebar.")
    st.stop()

with st.spinner("🛰️ Fetching orbital data from CelesTrak…"):
    df = fetch_data(tuple(selected_groups))

if df.empty:
    st.error("❌ Failed to load data. Check your internet connection and try refreshing.")
    st.stop()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
total     = len(df)
n_debris  = len(df[df["group"].str.contains("debris")])
n_sats    = total - n_debris
avg_alt   = df["alt_km"].mean()
max_alt   = df["alt_km"].max()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🛰️ Total Objects",   f"{total:,}")
col2.metric("🗑️ Debris Objects",  f"{n_debris:,}")
col3.metric("✅ Active Satellites", f"{n_sats:,}")
col4.metric("📏 Avg Altitude",     f"{avg_alt:,.0f} km")

st.divider()

# ---------------------------------------------------------------------------
# Risk Engine
# ---------------------------------------------------------------------------
risk_df = pd.DataFrame()
if run_risk:
    with st.spinner(f"⚠️ Running conjunction assessment (threshold: {threshold} km)…"):
        risk_df = compute_distances(df, threshold_km=threshold)
    summary = risk_summary(risk_df)

    if summary["total"] > 0:
        st.markdown(
            f"<div class='risk-banner'>"
            f"⚠️ <b>{summary['total']} conjunction pairs</b> found below {threshold} km "
            f"— CRITICAL: {summary['critical']} | HIGH: {summary['high']} | MEDIUM: {summary['medium']}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.success(f"✅ No conjunctions found below {threshold} km.")

# ---------------------------------------------------------------------------
# Globe
# ---------------------------------------------------------------------------
st.markdown("### 🌐 3D Orbital Globe")

figure_func = build_risk_globe_figure if (run_risk and not risk_df.empty) else build_globe_figure

if run_risk and not risk_df.empty:
    fig = build_risk_globe_figure(df, risk_df)
else:
    fig = build_globe_figure(df)

fig.update_layout(height=680)
st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# ---------------------------------------------------------------------------
# Risk Table
# ---------------------------------------------------------------------------
if run_risk and not risk_df.empty:
    st.divider()
    st.markdown("### ⚠️ Conjunction Report")

    # Color coding
    def style_risk(val):
        colors = {"CRITICAL": "#ff2222", "HIGH": "#ff8800", "MEDIUM": "#ffcc00"}
        return f"color: {colors.get(val, '#ffffff')}; font-weight: bold"

    styled = (
        risk_df.style
        .applymap(style_risk, subset=["risk_level"])
        .format({"distance_km": "{:.3f}"})
    )
    st.dataframe(styled, use_container_width=True, height=340)

    csv_bytes = risk_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Risk Report (CSV)",
        data=csv_bytes,
        file_name="conjunction_report.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Data Table
# ---------------------------------------------------------------------------
st.divider()
with st.expander("📊 Raw Orbital Data Table", expanded=False):
    display_df = df[["name", "lat", "lon", "alt_km", "type_label"]].copy()
    display_df.columns = ["Name", "Latitude (°)", "Longitude (°)", "Altitude (km)", "Type"]
    st.dataframe(
        display_df.style.format({"Latitude (°)": "{:.4f}", "Longitude (°)": "{:.4f}", "Altitude (km)": "{:.1f}"}),
        use_container_width=True,
        height=300,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center; color:#445566; font-size:0.75rem;'>"
    "Data: <a href='https://celestrak.org' style='color:#5577aa;'>CelesTrak / NORAD</a> "
    "• Propagation: SGP4 via Skyfield "
    "• Built by Furkan Onur"
    "</p>",
    unsafe_allow_html=True,
)
