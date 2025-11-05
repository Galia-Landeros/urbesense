from pathlib import Path
import pandas as pd
import numpy as np
from typing import Literal, Sequence

# Importa tu cálculo (usa tu mismo archivo que pegaste)
from src.calculariac import calcular_iac_impacto_df

# --- Geometría local para "repulsión" de puntos ---
KM_PER_DEG_LAT = 110.574

def _deg_lon_per_km(lat_deg: float) -> float:
    # 1° lon ≈ 111.320 * cos(lat) km  →  (° por km)
    return 1.0 / (111.320 * np.cos(np.radians(lat_deg)))

def _spread_points(df, min_dist_m: float = 500, max_iter: int = 120, step_frac: float = 0.35):
    """
    Empuja ligeramente los puntos (lat, lon) hasta que estén separados al menos 'min_dist_m'.
    No toca otras columnas. Aproximación planar alrededor del promedio.
    """
    if df.empty or len(df) <= 1:
        return df

    pts = df[["lat","lon"]].to_numpy(dtype=float)

    # Conversión local de metros ↔ grados
    lat0 = float(np.mean(pts[:,0]))
    deg_per_m_lat = 1.0 / (KM_PER_DEG_LAT * 1000.0)     # °lat por metro
    deg_per_m_lon = _deg_lon_per_km(lat0) / 1000.0      # °lon por metro
    min_d2 = (min_dist_m ** 2)

    for _ in range(max_iter):
        moved = 0
        for i in range(len(pts)):
            rx = ry = 0.0  # vector de repulsión acumulado (en metros)
            for j in range(len(pts)):
                if i == j:
                    continue
                dlat_m = (pts[i,0] - pts[j,0]) / deg_per_m_lat
                dlon_m = (pts[i,1] - pts[j,1]) / deg_per_m_lon
                d2 = dlat_m*dlat_m + dlon_m*dlon_m

                if d2 < 1e-6:
                    rx += 0.5; ry -= 0.5
                elif d2 < min_d2:
                    inv = (min_d2/d2) - 1.0
                    norm = np.sqrt(d2)
                    rx += (dlat_m/norm) * inv
                    ry += (dlon_m/norm) * inv

            if rx or ry:
                pts[i,0] += (rx * step_frac) * deg_per_m_lat
                pts[i,1] += (ry * step_frac) * deg_per_m_lon
                moved += 1
        if moved == 0:
            break

    out = df.copy()
    out["lat"] = pts[:,0]
    out["lon"] = pts[:,1]
    return out


# ---- Esquemas de columnas ----
REQUIRED_SEED: Sequence[str] = [
    "zona_id","nombre","lat","lon","co2","ruido","temperatura","seguridad"
]

REQUIRED_METRICS: Sequence[str] = [
    "zona_id","nombre","lat","lon","co2","ruido","temperatura","seguridad",
    "iac","impacto"
]

def _coerce_numeric(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def cargar_df(
    csv_path: str | Path = "data/zona.csv",
    iac_umbral: float = 0.35,
    mode: Literal["auto","seed","metrics"] = "auto",
    apply_spread: bool = True,
    min_dist_m: float = 500,
) -> pd.DataFrame:
    """
    Lee un CSV y devuelve DF listo para el mapa.

    - mode="auto": detecta si el CSV es seed (sin iac/impacto) o metrics (con iac/impacto).
    - mode="seed": fuerza a tratarlo como seed → calcula iac/impacto con calcular_iac_impacto_df.
    - mode="metrics": espera iac/impacto ya presentes.

    Añade:
      - estado ('activa'/'inactiva') y 'activa' (bool) según iac_umbral (en 0–100).
    """

    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el archivo '{p}'. Genera primero zona.csv (seed).")

    df = pd.read_csv(p)
    df.columns = [c.strip().lower() for c in df.columns]
    cols = set(df.columns)

    def _ensure(cols_needed: Sequence[str], nombre: str):
        missing = [c for c in cols_needed if c not in cols]
        if missing:
            raise ValueError(f"CSV incompleto para {nombre}. Faltan: {missing}")

    # Detectar modo
    if mode == "auto":
        if {"iac","impacto"}.issubset(cols):
            mode = "metrics"
        else:
            mode = "seed"

    # Seed → calcular iac/impacto
    if mode == "seed":
        _ensure(REQUIRED_SEED, "seed")
        _coerce_numeric(df, ["lat","lon","co2","ruido","temperatura","seguridad"])
        df = df.dropna(subset=["lat","lon","co2","ruido","temperatura","seguridad"]).copy()

        # Calcula IAC/Impacto usando TU lógica
        df = calcular_iac_impacto_df(df)

    elif mode == "metrics":
        _ensure(REQUIRED_METRICS, "metrics")
        _coerce_numeric(df, ["lat","lon","co2","ruido","temperatura","seguridad","iac","impacto"])
        df = df.dropna(subset=["lat","lon","iac","impacto"]).copy()

    # Spread (para que no se encimen)
    if apply_spread:
        df = _spread_points(df, min_dist_m=min_dist_m)

    # Soporte: si pasas umbral en 0–1, lo llevo a 0–100.
    if 0.0 <= iac_umbral <= 1.0:
        thr = iac_umbral * 100.0
    else:
        thr = iac_umbral
    df["estado"] = df["iac"].apply(lambda v: "activa" if float(v) >= thr else "inactiva")
    df["activa"] = (df["estado"] == "activa")

    # Orden sugerido
    order = [
        "zona_id","nombre","lat","lon","co2","ruido","temperatura","seguridad",
        "iac","impacto","estado","activa"
    ]
    cols_out = [c for c in order if c in df.columns] + [c for c in df.columns if c not in order]
    return df.loc[:, cols_out].reset_index(drop=True)
