#aqui leo la data
##objetivo: 1-Leer el CSV 2-validar que esten en las columnas correctas 3-limpiar datos basicos(Nan, tipos)
"""Carga y validación de datasets."""
import pandas as pd
from .config import EXPECTED_COLUMNS

def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    miss = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if miss:
        raise ValueError(f"Faltan columnas obligatorias: {miss}")
    return df
