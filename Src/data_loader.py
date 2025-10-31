# src/data_loader.py
from pathlib import Path
import pandas as pd

REQUIRED = ["zona_id","nombre","lat","lon","co2","ruido","temperatura","seguridad"]

def load_zonas_csv(csv_path: str | Path = "data/zonas.csv") -> pd.DataFrame:
    p = Path(csv_path)
    df = pd.read_csv(p)
    df.columns = [c.strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV incompleto, faltan: {missing}")

    # tipos seguros
    for c in ["lat","lon","co2","ruido","temperatura","seguridad"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["lat","lon","co2","ruido","temperatura","seguridad"]).copy()

    # (opcional) si quieres limitar a 10 más cercanas al centro de Campeche
    # from src.config import CENTER
    # lat0, lon0 = CENTER["lat"], CENTER["lon"]
    # df["d2"] = (df["lat"]-lat0)**2 + (df["lon"]-lon0)**2
    # df = df.sort_values("d2").head(10).drop(columns="d2")

    return df.reset_index(drop=True)

