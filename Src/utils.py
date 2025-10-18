"""Utilidades: validaciones y helpers simples."""
from typing import Iterable, List

def missing_columns(cols: Iterable[str], expected: Iterable[str]) -> List[str]:
    cols = list(cols)
    expected = list(expected)
    return [c for c in expected if c not in cols]

def color_from_iac(iac: float, hi: int = 70, mid: int = 40) -> str:
    # Colores para Plotly (hex)
    if iac >= hi:  return "#2ECC71"  # verde
    if iac >= mid: return "#F1C40F"  # amarillo
    return "#E74C3C"                 # rojo