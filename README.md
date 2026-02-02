# Orbital Debris & Satellite Tracker

### Project Overview
This project is a Python-based astrodynamics tool designed to visualize and analyze Low Earth Orbit (LEO) objects in real-time. Utilizing **NASA/CelesTrak TLE data**, it performs orbital propagation to map the current positions of active satellites and space debris.

The ultimate goal is to develop a **Conjunction Assessment** system that identifies potential collision risks between space assets and debris fields.

### Tech Stack
* **Language:** Python 3.14.2
* **Orbital Mechanics:** `Skyfield` (SGP4 propagation, WGS84 coordinate systems)
* **Data Processing:** `Pandas` (ETL pipeline for TLE data)
* **Visualization:** `Plotly` (Interactive 3D Geospatial mapping)
* **Data Source:** CelesTrak (NORAD GP Element Sets)

### Current Status & Roadmap

#### Phase 1: Core Engine (In Progress)
- [x] Fetch real-time TLE data from CelesTrak.
- [x] Parse TLE data into Skyfield EarthSatellite objects.
- [x] Calculate Geocentric (GCRS) vectors based on current Epoch.
- [x] Convert vectors to Geodetic coordinates (Latitude/Longitude/Altitude) using WGS84 model.
- [x] Clean and structure data using Pandas DataFrames.
- [ ] Visualizing objects on a 3D Earth Map using Plotly.

#### Phase 2: Web Application (Planned)
- [ ] Migrate the visualization to a **Streamlit** web interface.
- [ ] Implement interactive filters (e.g., Show only Debris, Show only Space Stations).

#### Phase 3: Risk Analysis (Planned)
- [ ] Develop a **Proximity Calculator** to detect close approaches.
- [ ] Visualize "High Risk" objects (objects < 100km apart) in red.
- [ ] Implement a user-click callback to show specific orbital parameters.

### How to Run
1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)[furkanonur-ds-space]/Orbital-Debris-Tracker.git
2. Install dependencies:
    ```bash
    pip install skyfield pandas plotly
3. Run the tracker:
    ```bash
    python tracker.py

### Author
- Furkan Onur