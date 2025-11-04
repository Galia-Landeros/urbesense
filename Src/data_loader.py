# src/data_loader.py
from pathlib import Path
import pandas as pd
import numpy as np

KM_PER_DEG_LAT = 110.574
def _deg_lon_per_km(lat_deg: float) -> float:
    # 1° lon ≈ 111.320 * cos(lat) km  →  km por 1° lon  →  (° por km) = 1 / km_por_grado
    return 1.0 / (111.320 * np.cos(np.radians(lat_deg)))

def _spread_points(df, min_dist_m: float = 500, max_iter: int = 120, step_frac: float = 0.35):
    """
    Empuja ligeramente los puntos (lat, lon) hasta que estén separados al menos 'min_dist_m'.
    - No toca otras columnas.
    - max_iter limita el tiempo de relajación.
    - step_frac controla qué tan grandes son los pasos (0.25–0.5 suele ir bien).
    """
    if df.empty or len(df) <= 1:
        return df

    pts = df[["lat","lon"]].to_numpy(dtype=float)

    # Conversión local de metros ↔ grados (aprox. planar alrededor del promedio)
    lat0 = float(np.mean(pts[:,0]))
    deg_per_m_lat = 1.0 / (KM_PER_DEG_LAT * 1000.0)          # °lat por metro
    deg_per_m_lon = _deg_lon_per_km(lat0) / 1000.0           # °lon por metro
    min_d2 = (min_dist_m ** 2)

    for _ in range(max_iter):
        moved = 0
        for i in range(len(pts)):
            rx = ry = 0.0  # vector de repulsión acumulado (en metros)
            for j in range(len(pts)):
                if i == j: 
                    continue
                # Distancia aproximada (en metros) usando escala local
                dlat_m = (pts[i,0] - pts[j,0]) / deg_per_m_lat
                dlon_m = (pts[i,1] - pts[j,1]) / deg_per_m_lon
                d2 = dlat_m*dlat_m + dlon_m*dlon_m

                if d2 < 1e-6:
                    # superpuestos exactos: empujón mínimo determinista
                    rx += 0.5; ry -= 0.5
                elif d2 < min_d2:
                    # empuje radial suave: cuanto más cerca, más empuje
                    inv = (min_d2/d2) - 1.0
                    norm = np.sqrt(d2)
                    rx += (dlat_m/norm) * inv
                    ry += (dlon_m/norm) * inv

            if rx or ry:
                # aplicar paso (convertimos de metros a grados)
                pts[i,0] += (rx * step_frac) * deg_per_m_lat
                pts[i,1] += (ry * step_frac) * deg_per_m_lon
                moved += 1
        if moved == 0:
            break

    out = df.copy()
    out["lat"] = pts[:,0]
    out["lon"] = pts[:,1]
    return out



REQUIRED = ["zona_id","nombre","lat","lon","co2","ruido","temperatura","seguridad"]

# límites geográficos seguros en tierra (ajustados con tus datos reales)
LAT_MIN, LAT_MAX = 19.832, 19.860  # <- empuja fuera del agua
LON_MIN, LON_MAX = -90.560, -90.510  # <- opcional para recortar demasiado al este/oeste



def load_zonas_csv(csv_path: str | Path = "data/zona.csv") -> pd.DataFrame:
    p = Path(csv_path)
    df = pd.read_csv(p)

    # normaliza headers
    df.columns = [c.strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV incompleto, faltan: {missing}")

    # asegurar tipo numérico
    for c in ["lat","lon","co2","ruido","temperatura","seguridad"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop filas jodidas
    df = df.dropna(subset=["lat","lon","co2","ruido","temperatura","seguridad"]).copy()

    # (opcional) límites geográficos dentro de Campeche
    LAT_MIN, LAT_MAX = 19.832, 19.860
    LON_MIN, LON_MAX = -90.560, -90.510
    df["lat"] = df["lat"].clip(LAT_MIN, LAT_MAX)
    df["lon"] = df["lon"].clip(LON_MIN, LON_MAX)

    # 🔥 Aplica repulsión suave
    df = _spread_points(df, min_dist_m=500)

    # (opcional) si quieres solo 10 más cercanas al centro:
    # lat0, lon0 = 19.845, -90.535
    # df["d2"] = (df["lat"]-lat0)**2 + (df["lon"]-lon0)**2
    # df = df.sort_values("d2").head(10).drop(columns="d2")

    return df.reset_index(drop=True)


