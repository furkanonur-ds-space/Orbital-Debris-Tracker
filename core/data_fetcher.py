"""
data_fetcher.py
---------------
Responsible for fetching TLE data from CelesTrak and building
a structured Pandas DataFrame with orbital parameters.

Data Sources (CelesTrak GP element sets):
  - stations      : Space Stations (ISS, CSS, etc.)
  - active        : All Active Satellites
  - cosmos-1408-debris : Russian ASAT test debris
  - fengyun-1c-debris  : Chinese ASAT test debris
  - iridium-33-debris  : Iridium 33 collision debris
  - cosmos-2251-debris : Cosmos 2251 collision debris
"""

import logging
import pandas as pd
from skyfield.api import load, wgs84, EarthSatellite

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CelesTrak TLE endpoint (GP format, TLE style)
# ---------------------------------------------------------------------------
CELESTRAK_BASE = "https://celestrak.org/NORAD/elements/gp.php"

# Human-readable labels for each data group
GROUP_LABELS: dict[str, str] = {
    "stations": "Space Station",
    "active": "Active Satellite",
    "cosmos-1408-debris": "Debris (Cosmos-1408)",
    "fengyun-1c-debris": "Debris (Fengyun-1C)",
    "iridium-33-debris": "Debris (Iridium-33)",
    "cosmos-2251-debris": "Debris (Cosmos-2251)",
}

# Color map used by the visualizer – keeps palette in one place
GROUP_COLORS: dict[str, str] = {
    "stations": "#FFA500",          # Orange
    "active": "#00BFFF",            # Deep Sky Blue
    "cosmos-1408-debris": "#FF4444",
    "fengyun-1c-debris": "#FF6666",
    "iridium-33-debris": "#FF8888",
    "cosmos-2251-debris": "#FFAAAA",
}


# ---------------------------------------------------------------------------
# TLE Fetching
# ---------------------------------------------------------------------------

def fetch_tle_group(group: str) -> dict[str, EarthSatellite]:
    """
    Download TLE data for the given CelesTrak group and return a dict
    mapping satellite name -> EarthSatellite object.

    Parameters
    ----------
    group : str
        CelesTrak group key (e.g. 'stations', 'active').

    Returns
    -------
    dict[str, EarthSatellite]
        Empty dict on failure.
    """
    url = f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=tle"
    logger.info("Fetching TLE data: group='%s' from %s", group, url)
    try:
        satellites = load.tle_file(url, reload=True)
        sat_dict = {sat.name: sat for sat in satellites}
        logger.info("Loaded %d objects from group '%s'", len(sat_dict), group)
        return sat_dict
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch group '%s': %s", group, exc)
        return {}


# ---------------------------------------------------------------------------
# DataFrame Builder
# ---------------------------------------------------------------------------

def build_dataframe(
    sat_dict: dict[str, EarthSatellite],
    ts,
    group_key: str = "unknown",
) -> pd.DataFrame:
    """
    Propagate every satellite to the current epoch and return a DataFrame
    with geodetic coordinates and metadata.

    Columns
    -------
    name        : str   – satellite name
    lat         : float – geodetic latitude  (degrees)
    lon         : float – geodetic longitude (degrees)
    alt_km      : float – altitude above WGS-84 ellipsoid (km)
    group       : str   – CelesTrak group key
    type_label  : str   – human-readable object type
    color       : str   – hex color for the visualizer
    """
    t = ts.now()
    records = []

    for name, sat in sat_dict.items():
        try:
            geocentric = sat.at(t)
            subpoint = wgs84.subpoint(geocentric)
            records.append(
                {
                    "name": name,
                    "lat": subpoint.latitude.degrees,
                    "lon": subpoint.longitude.degrees,
                    "alt_km": subpoint.elevation.km,
                    "group": group_key,
                    "type_label": GROUP_LABELS.get(group_key, group_key),
                    "color": GROUP_COLORS.get(group_key, "#AAAAAA"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Skipping '%s': %s", name, exc)

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(subset="name").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Convenience: load multiple groups at once
# ---------------------------------------------------------------------------

def load_groups(groups: list[str], ts) -> pd.DataFrame:
    """
    Fetch and combine multiple CelesTrak groups into one DataFrame.

    Parameters
    ----------
    groups : list[str]
        List of group keys to fetch.
    ts     : Skyfield Timescale
        Skyfield timescale object.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame, may be empty if all fetches fail.
    """
    frames: list[pd.DataFrame] = []
    for group in groups:
        sat_dict = fetch_tle_group(group)
        if sat_dict:
            frames.append(build_dataframe(sat_dict, ts, group_key=group))

    if not frames:
        logger.warning("No data loaded from any group.")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Total objects loaded: %d", len(combined))
    return combined
