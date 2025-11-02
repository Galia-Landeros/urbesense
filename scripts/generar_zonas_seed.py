# scripts/generar_zonas_seed.py
"""
Genera un CSV con entradas base para el proyecto (opción híbrida):
  columnas: zona_id, nombre, lat, lon, co2, ruido, temperatura, seguridad

- Usa los rangos definidos en src/calculariac.py (si existen).
- Posiciona 10 zonas alrededor del centro de Campeche (configurable).
- No calcula IAC ni Impacto (se calculan en runtime en el dashboard).
"""

from __future__ import annotations
import argparse
import math
from pathlib import Path
import pandas as pd
import numpy as np

# ---------------------------
# Parámetros por defecto
# ---------------------------
DEFAULT_OUT = Path("data/zona.csv")
CENTER = {"lat": 19.845, "lon": -90.535}  # Campeche capital
R_MIN_KM, R_MAX_KM = 0.7, 3.5             # anillo donde caerán las zonas
DEFAULT_N = 10                             # 🔹 Ahora 10 zonas por defecto
DEFAULT_SEED = 42

# ---------------------------
# Intenta leer rangos desde src/calculariac.py
# ---------------------------
def load_ranges_from_module():
    try:
        from src.calculariac import CO2_RANGE, RUIDO_RANGE, TEMP_MINMAX  # type: ignore
        return {
            "co2": CO2_RANGE,         # (400, 1200)
            "ruido": RUIDO_RANGE,     # (40, 90)
            "temp_minmax": TEMP_MINMAX,  # (15, 35)
            "seguridad": (0, 100)
        }
    except Exception:
        return {
            "co2": (400.0, 1200.0),
            "ruido": (40.0, 90.0),
            "temp_minmax": (15.0, 35.0),
            "seguridad": (0.0, 100.0),
        }

RNGS = load_ranges_from_module()

# ---------------------------
# Helpers geográficos
# ---------------------------
def km_to_deg_lat(km: float) -> float:
    return km / 110.574

def km_to_deg_lon(km: float, lat_deg: float) -> float:
    return km / (111.320 * math.cos(math.radians(lat_deg)))

def radial_points(center_lat, center_lon, n, rmin_km, rmax_km, rng):
    base_angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    jitter = rng.normal(loc=0.0, scale=0.12, size=n)
    angles = (base_angles + jitter) % (2*np.pi)

    # 👉 limitamos ángulos a semicírculo sur-este (evita mar)
    valid = []
    for th in angles:
        # solo cuadrantes sur (pi/2–3pi/2) y este (0–pi/2)
        if np.pi/2 <= th <= 3*np.pi/2:
            valid.append(th)
        else:
            valid.append(th + np.pi/2)
    angles = np.array(valid)

    radii = rng.uniform(rmin_km, rmax_km, size=n)

    lats, lons = [], []
    for r_km, th in zip(radii, angles):
        dlat = km_to_deg_lat(r_km * math.sin(th))
        dlon = km_to_deg_lon(r_km * math.cos(th), center_lat)
        lats.append(center_lat + dlat)
        lons.append(center_lon + dlon)
    return np.array(lats), np.array(lons)


# ---------------------------
# Generadores de variables
# ---------------------------
def sample_co2(n: int, rng: np.random.Generator, lo: float, hi: float) -> np.ndarray:
    mu = (lo + hi) / 2
    sigma = (hi - lo) / 6
    vals = rng.normal(mu, sigma, size=n)
    return np.clip(vals, lo, hi).round()

def sample_ruido(n: int, rng: np.random.Generator, lo: float, hi: float) -> np.ndarray:
    mu = (lo + hi) * 0.55
    sigma = (hi - lo) / 7
    vals = rng.normal(mu, sigma, size=n)
    return np.clip(vals, lo, hi).round(0)

def sample_temp(n: int, rng: np.random.Generator, tmin: float, tmax: float) -> np.ndarray:
    mu = 28.0
    sigma = 3.2
    vals = rng.normal(mu, sigma, size=n)
    return np.clip(vals, tmin, tmax).round(1)

def sample_seguridad(n: int, rng: np.random.Generator, lo: float, hi: float) -> np.ndarray:
    base = rng.uniform(55, 85, size=n)
    jitter = rng.normal(0, 6, size=n)
    vals = np.clip(base + jitter, lo, hi)
    return np.round(vals, 0)

# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Genera data/zonas.csv con 10 zonas (entradas base, sin IAC/Impacto).")
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Número de zonas a generar (default: 10)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Semilla RNG (default: 42)")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT), help="Ruta de salida CSV (default: data/zonas.csv)")
    parser.add_argument("--center-lat", type=float, default=CENTER["lat"], help="Centro latitud (default: 19.845)")
    parser.add_argument("--center-lon", type=float, default=CENTER["lon"], help="Centro longitud (default: -90.535)")
    parser.add_argument("--rminkm", type=float, default=R_MIN_KM, help="Radio mínimo en km (default: 0.7)")
    parser.add_argument("--rmaxkm", type=float, default=R_MAX_KM, help="Radio máximo en km (default: 3.5)")
    args = parser.parse_args()

    n = max(1, int(args.n))
    rng = np.random.default_rng(args.seed)

    # Posiciones
    lats, lons = radial_points(args.center_lat, args.center_lon, n, args.rminkm, args.rmaxkm, rng)

    # Rangos
    co2_lo, co2_hi = RNGS["co2"]
    ru_lo, ru_hi = RNGS["ruido"]
    tmin, tmax = RNGS["temp_minmax"]
    seg_lo, seg_hi = RNGS["seguridad"]

    # Muestras
    co2 = sample_co2(n, rng, co2_lo, co2_hi).astype(int)
    ruido = sample_ruido(n, rng, ru_lo, ru_hi).astype(int)
    temp = sample_temp(n, rng, tmin, tmax).astype(float)
    seg  = sample_seguridad(n, rng, seg_lo, seg_hi).astype(int)

    # DataFrame final (entradas SOLAMENTE)
    df = pd.DataFrame({
        "zona_id": np.arange(1, n+1, dtype=int),
        "nombre": [f"Zona {i}" for i in range(1, n+1)],
        "lat": lats.round(6),
        "lon": lons.round(6),
        "co2": co2,
        "ruido": ruido,
        "temperatura": temp,
        "seguridad": seg
    })
# ...existing code...
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote CSV to {out_path}")
# ...existing code...
if __name__ == "__main__":
    main()