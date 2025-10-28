# src/simulate_geo.py  (o core/simulate_geo.py si cambias el import)
import numpy as np
import pandas as pd
from datetime import datetime

__all__ = ["CAMPECHE_CENTER", "simulate_campeche_capital", "save_simulation_csv"]

# Centro por defecto: Campeche capital
CAMPECHE_CENTER = {"lat": 19.845, "lon": -90.535}

# Helpers geo (aprox. buenos a escala urbana)
def km_to_deg_lat(km):         # 1° lat ~ 110.574 km
    return km / 110.574
def km_to_deg_lon(km, lat_deg):# 1° lon ~ 111.320 * cos(lat)
    return km / (111.320 * np.cos(np.radians(lat_deg)))
def polar_offset(lat0, lon0, r_km, theta_rad):
    dlat = km_to_deg_lat(r_km) * np.sin(theta_rad)
    dlon = km_to_deg_lon(r_km, lat0) * np.cos(theta_rad)
    return lat0 + dlat, lon0 + dlon

def simulate_campeche_capital(
    n_colonias: int = 12,
    puntos_por_colonia: int = 4,
    radio_min_km: float = 0.6,
    radio_max_km: float = 8.0,
    center_lat: float = CAMPECHE_CENTER["lat"],
    center_lon: float = CAMPECHE_CENTER["lon"],
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Genera clusters tipo 'colonias' alrededor del centro de Campeche capital.
    """
    rng = np.random.default_rng(seed)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    # 1) Sembrar centros de colonia en anillos
    colonias = []
    n_anillos = max(1, int(np.ceil(n_colonias / 6)))
    radios = np.linspace(radio_min_km, radio_max_km, n_anillos)
    idx = 0
    for r in radios:
        n_en_anillo = min(6, n_colonias - idx)
        if n_en_anillo <= 0:
            break
        thetas = np.linspace(0, 2*np.pi, n_en_anillo, endpoint=False) + rng.normal(0, 0.18, n_en_anillo)
        for th in thetas:
            latc, lonc = polar_offset(center_lat, center_lon, r, th)
            idx += 1
            colonias.append({"col_id": idx, "colonia": f"Colonia {idx}", "lat_c": latc, "lon_c": lonc})

    # 2) Generar puntos alrededor del centro de cada colonia
    rows, zona_id = [], 1
    for c in colonias:
        iac_base = rng.uniform(25, 85)  # “personalidad” de la colonia
        for _ in range(puntos_por_colonia):
            r_local = rng.uniform(0.05, 0.7)     # radio local en km
            th_local = rng.uniform(0, 2*np.pi)
            lat, lon = polar_offset(c["lat_c"], c["lon_c"], r_local, th_local)

            # Métricas coherentes y acotadas
            iac   = float(np.clip(iac_base + rng.normal(0, 8), 0, 100))
            co2   = float(np.clip(rng.normal(650 + (80 - iac)*4, 100), 300, 2000))
            ruido = float(np.clip(rng.normal(48 + iac*0.28, 7), 30, 100))
            temp  = float(np.clip(rng.normal(27, 1.6), 15, 35))

            rows.append({
                "zona_id": zona_id,
                "nombre": c["colonia"],  # agrupador visible
                "lat": lat, "lon": lon,
                "iac": iac, "ruido": ruido, "co2": co2, "temperatura": temp,
                "fecha": now.strftime("%Y-%m-%d"), "hora": now.strftime("%H:%M"),
                "col_id": c["col_id"], "colonia": c["colonia"],
            })
            zona_id += 1

    return pd.DataFrame(rows)

def save_simulation_csv(df: pd.DataFrame, path: str = "data/urbansense.csv") -> None:
    df.to_csv(path, index=False)

