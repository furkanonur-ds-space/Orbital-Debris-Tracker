"""
risk_engine.py
--------------
Phase 3: Conjunction Assessment Engine.

Computes pairwise distances between tracked objects and flags
pairs whose closest approach falls below a configurable threshold.

Algorithm
---------
1. Convert (lat, lon, alt) → Cartesian ECEF (km) using WGS-84.
2. Compute Euclidean distances between every pair.
3. Return pairs below the threshold sorted by distance ascending.

Performance note
-----------------
Brute-force O(n²) — fine for hundreds of objects (station/debris groups).
For full active satellite sets (10 000+ objects) this should be replaced
with a KD-Tree spatial index. See ``compute_distances_fast`` below.
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# WGS-84 semi-major axis
_WGS84_A_KM = 6378.137
_WGS84_B_KM = 6356.752


# ---------------------------------------------------------------------------
# Coordinate helper
# ---------------------------------------------------------------------------

def _geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_km: float) -> np.ndarray:
    """
    Convert geodetic coordinates to Earth-Centered Earth-Fixed (km).

    Parameters
    ----------
    lat_deg, lon_deg : degrees
    alt_km           : km above ellipsoid

    Returns
    -------
    np.ndarray  shape (3,)  [x, y, z] in km
    """
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)

    e2 = 1 - (_WGS84_B_KM / _WGS84_A_KM) ** 2
    N = _WGS84_A_KM / np.sqrt(1 - e2 * np.sin(lat) ** 2)

    x = (N + alt_km) * np.cos(lat) * np.cos(lon)
    y = (N + alt_km) * np.cos(lat) * np.sin(lon)
    z = (N * (1 - e2) + alt_km) * np.sin(lat)

    return np.array([x, y, z])


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------

def compute_distances(df: pd.DataFrame, threshold_km: float = 100.0) -> pd.DataFrame:
    """
    Find all object pairs closer than ``threshold_km``.

    Parameters
    ----------
    df           : pd.DataFrame
        Must contain: name, lat, lon, alt_km, type_label.
    threshold_km : float
        Conjunction distance threshold in km. Default 100.

    Returns
    -------
    pd.DataFrame with columns:
        name_a, name_b, type_a, type_b, distance_km, risk_level
    Sorted by distance_km ascending.
    """
    if df.empty or len(df) < 2:
        logger.warning("Not enough objects to compute distances.")
        return pd.DataFrame()

    logger.info("Computing ECEF positions for %d objects …", len(df))

    # Vectorised ECEF conversion
    lat = np.radians(df["lat"].values)
    lon = np.radians(df["lon"].values)
    alt = df["alt_km"].values

    e2 = 1 - (_WGS84_B_KM / _WGS84_A_KM) ** 2
    N = _WGS84_A_KM / np.sqrt(1 - e2 * np.sin(lat) ** 2)

    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = (N * (1 - e2) + alt) * np.sin(lat)

    coords = np.column_stack([x, y, z])   # shape (n, 3)
    names = df["name"].values
    types = df["type_label"].values

    n = len(coords)
    logger.info("Scanning %d object pairs (threshold %.0f km) …", n * (n - 1) // 2, threshold_km)

    results = []
    for i in range(n):
        # Vectorised distance from object i to all j > i
        diff = coords[i] - coords[i + 1 :]
        dists = np.linalg.norm(diff, axis=1)
        close_mask = dists < threshold_km

        for offset, dist in enumerate(dists[close_mask]):
            j = i + 1 + np.where(close_mask)[0][offset]
            results.append(
                {
                    "name_a": names[i],
                    "name_b": names[j],
                    "type_a": types[i],
                    "type_b": types[j],
                    "distance_km": round(float(dist), 3),
                    "risk_level": _risk_level(dist),
                }
            )

    if not results:
        logger.info("No conjunctions found below %.0f km.", threshold_km)
        return pd.DataFrame(
            columns=["name_a", "name_b", "type_a", "type_b", "distance_km", "risk_level"]
        )

    out = pd.DataFrame(results).sort_values("distance_km").reset_index(drop=True)
    logger.info("Found %d conjunction pairs.", len(out))
    return out


def _risk_level(dist_km: float) -> str:
    """Classify risk by distance."""
    if dist_km < 10:
        return "CRITICAL"
    if dist_km < 50:
        return "HIGH"
    return "MEDIUM"


# ---------------------------------------------------------------------------
# Summary helpers for Streamlit
# ---------------------------------------------------------------------------

def risk_summary(risk_df: pd.DataFrame) -> dict:
    """
    Return counts per risk level for display in the UI.

    Returns
    -------
    dict with keys: total, critical, high, medium
    """
    if risk_df.empty:
        return {"total": 0, "critical": 0, "high": 0, "medium": 0}

    counts = risk_df["risk_level"].value_counts()
    return {
        "total": len(risk_df),
        "critical": int(counts.get("CRITICAL", 0)),
        "high": int(counts.get("HIGH", 0)),
        "medium": int(counts.get("MEDIUM", 0)),
    }
