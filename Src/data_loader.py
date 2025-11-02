# src/data_loader.py
from pathlib import Path
import pandas as pd

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

    # 👇 CLAMP GEO AQUÍ
    df["lat"] = df["lat"].clip(LAT_MIN, LAT_MAX)
    df["lon"] = df["lon"].clip(LON_MIN, LON_MAX)

    # (opcional) si quieres solo 10 más cercanas al centro:
    # lat0, lon0 = 19.845, -90.535
    # df["d2"] = (df["lat"]-lat0)**2 + (df["lon"]-lon0)**2
    # df = df.sort_values("d2").head(10).drop(columns="d2")

    return df.reset_index(drop=True)


