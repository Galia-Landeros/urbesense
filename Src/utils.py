"""Utilidades: validaciones y helpers simples."""
from typing import Iterable, List
import pandas as pd
import os
from pathlib import Path

def file_signature(path: str | os.PathLike):
    p = Path(path)
    if not p.exists():
        return None
    stat = p.stat()
    return (int(stat.st_mtime), int(stat.st_size))

def coerce_numeric(df: pd.DataFrame, cols):
    d = df.copy()
    for c in cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

def filter_df(df: pd.DataFrame, *, q=None, iac_min=0, iac_max=100, fecha_min=None, fecha_max=None):
    d = df.copy()
    if q:
        qlow = q.strip().lower()
        d = d[d["nombre"].astype(str).str.lower().str.contains(qlow)]
    d = d[(d["iac"] >= iac_min) & (d["iac"] <= iac_max)]
    if "fecha" in d.columns:
        d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")
        if fecha_min is not None: d = d[d["fecha"] >= pd.to_datetime(fecha_min)]
        if fecha_max is not None: d = d[d["fecha"] <= pd.to_datetime(fecha_max)]
    return d

def missing_columns(cols: Iterable[str], expected: Iterable[str]) -> List[str]:
    cols = list(cols)
    expected = list(expected)
    return [c for c in expected if c not in cols]

def color_from_iac(iac: float, hi: int = 70, mid: int = 40) -> str:
    # Colores para Plotly (hex)
    if iac >= hi:  return "#2ECC71"  # verde
    if iac >= mid: return "#F1C40F"  # amarillo
    return "#E74C3C"                 # rojo