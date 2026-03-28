# 🛰️ Orbital Debris & Satellite Tracker

> Real-time LEO object tracking, 3D visualization, and conjunction risk analysis using **NASA/CelesTrak TLE data** and **SGP4 orbital propagation**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) ![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?logo=streamlit) ![Plotly](https://img.shields.io/badge/Plotly-3D_Globe-3D4DB7?logo=plotly) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Features

| Feature | Status |
|---|---|
| Real-time TLE data from CelesTrak (6 object groups) | ✅ |
| SGP4 propagation → Geodetic coordinates (WGS-84) | ✅ |
| Interactive 3D orthographic globe (Plotly, dark theme) | ✅ |
| Streamlit web interface with live sidebar filters | ✅ |
| Conjunction Assessment — proximity flagging (< N km) | ✅ |
| High-risk object highlighting in RED on the globe | ✅ |
| Downloadable CSV conjunction risk report | ✅ |

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/furkanonur-ds-space/Orbital-Debris-Tracker.git
cd Orbital-Debris-Tracker
pip install -r requirements.txt
```

### 2. Run the web app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
SpaceDebrisProject/
├── core/
│   ├── __init__.py
│   ├── data_fetcher.py   # TLE ETL pipeline — CelesTrak API, multi-group
│   ├── visualizer.py     # Plotly 3D orthographic globe (dark theme)
│   └── risk_engine.py    # Conjunction assessment — ECEF distance engine
├── app.py                # Streamlit web application (all phases integrated)
├── requirements.txt
└── README.md
```

---

## 🔭 Data Sources

| CelesTrak Group | Description |
|---|---|
| `stations` | Space Stations (ISS, CSS …) |
| `active` | All active satellites |
| `cosmos-1408-debris` | Russian ASAT test debris (2021) |
| `fengyun-1c-debris` | Chinese ASAT test debris (2007) |
| `iridium-33-debris` | Iridium 33 collision debris (2009) |
| `cosmos-2251-debris` | Cosmos 2251 collision debris (2009) |

---

## ⚙️ Tech Stack

| Layer | Library |
|---|---|
| Orbital Mechanics | `skyfield` (SGP4, WGS-84) |
| Data Processing | `pandas`, `numpy` |
| Visualization | `plotly` (3D globe) |
| Web Interface | `streamlit` |
| Data Source | [CelesTrak](https://celestrak.org) / NORAD |

---

## 🗺️ Architecture

```
CelesTrak API (TLE data)
        │
        ▼
core/data_fetcher.py   → fetch → propagate → DataFrame
        │
        ├──▶ core/visualizer.py  → Plotly 3D orthographic globe
        │
        └──▶ core/risk_engine.py → Conjunction pairs (ECEF distances)
                        │
                        ▼
               app.py (Streamlit)  →  http://localhost:8501
```

---

## 🗓️ Roadmap

- [x] **Phase 1** — Core Engine: TLE fetch, SGP4 propagation, 3D globe visualization
- [x] **Phase 2** — Web Application: Streamlit UI, live filters, data refresh
- [x] **Phase 3** — Risk Analysis: Conjunction assessment, risk highlighting, CSV export
- [ ] **Phase 4** *(Future)* — KD-Tree optimisation for large datasets (10 000+ objects)
- [ ] **Phase 4** *(Future)* — Orbital parameter sidebar on object click

---

## 👤 Author

**Furkan Onur** — [GitHub](https://github.com/furkanonur-ds-space)