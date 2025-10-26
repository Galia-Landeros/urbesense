import pandas as pd

EXPECTED = ["zona_id","nombre","lat","lon","iac","ruido","co2","temperatura","fecha","hora"]

RENAME_MAP = {
    "zona": "nombre",
    "latitude": "lat",
    "latitud": "lat",
    "longitude": "lon",
    "longitud": "lon",
    "index_actividad": "iac",
    "indice_actividad": "iac",
}

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Limpia encabezados
    cols = (df.columns
              .str.strip()
              .str.lower()
              .str.replace("\ufeff", "", regex=False))
    df.columns = cols
    df = df.rename(columns=RENAME_MAP)
    return df

def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8", dtype=str)
    df = _normalize_columns(df)

    # Convierte tipos
    to_float = ["lat","lon","iac","ruido","co2","temperatura"]
    for c in to_float:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if "hora" in df.columns:
        df["hora"] = df["hora"].astype(str).str.strip()

    # Validación de columnas esenciales
    required = ["lat","lon","iac","nombre"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Faltan columnas requeridas en el CSV: {missing}. "
            f"Columnas detectadas: {list(df.columns)}"
        )

    df = df.dropna(subset=["lat","lon"])
<<<<<<< HEAD
    return df
=======
    return df
>>>>>>> 222f61efc4ee689fb8f343b4bb1a09687a22e75f
