# src/calculariac.py
"""
Cálculo en runtime del IAC (0–100, mayor = mejor) y del Impacto (0–100, mayor = peor),
más un simulador por deltas (CO₂, temperatura, ruido, seguridad).

Entradas esperadas por zona:
- co2 (ppm)              [~400–1200]
- ruido (dB)             [~40–90]
- temperatura (°C)       [~15–35], óptimo en 22–26
- seguridad (0–1 o 0–100)

Salidas añadidas al DataFrame:
- iac (0–100, mayor=mejor)
- impacto (0–100, mayor=peor)
- co2_n, ruido_n, temp_n, seg_n  (normalizados 0=bueno, 1=malo)

Uso típico:
    from src.calculariac import calcular_iac_impacto_df, aplicar_simulador
    df_calc = calcular_iac_impacto_df(df_raw)                # calcula IAC/Impacto
    df_sim  = aplicar_simulador(df_calc, d_co2=50, d_seg=-5) # aplica deltas y recalcula
"""

from __future__ import annotations
from typing import Iterable, Tuple
import numpy as np
import pandas as pd

# -------------------------------
# Parámetros (ajustables)
# -------------------------------
# Rangos de referencia para normalización
CO2_RANGE: Tuple[float, float]   = (400.0, 1200.0)  # ppm (400 bueno, 1200 malo)
RUIDO_RANGE: Tuple[float, float] = (40.0, 90.0)     # dB  (40 bueno, 90 malo)
TEMP_COMFORT: Tuple[float, float] = (22.0, 26.0)    # °C  (zona de confort)
TEMP_MINMAX: Tuple[float, float]  = (15.0, 35.0)    # °C  (extremos razonables)

# Pesos para el IAC (suma implícita)
# w1 = CO2, w2 = RUIDO, w3 = TEMP, w4 = SEGURIDAD
w1: float = 0.20
w2: float = 0.20
w3: float = 0.25
w4: float = 0.35

# Mezcla para Impacto (mayor = peor)
ALPHA_IAC: float = 0.60  # penaliza bajo IAC
ALPHA_SEG: float = 0.40  # penaliza inseguridad

# Columnas esperadas
EXPECTED_INPUT_COLS = ("co2", "ruido", "temperatura", "seguridad")

__all__ = [
    "CO2_RANGE", "RUIDO_RANGE", "TEMP_COMFORT", "TEMP_MINMAX",
    "w1", "w2", "w3", "w4", "ALPHA_IAC", "ALPHA_SEG",
    "calcular_iac", "calcular_impacto",
    "calcular_iac_impacto_df", "aplicar_simulador",
]


# -------------------------------
# Helpers
# -------------------------------
def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def _seg_to_0_100(seg: float) -> float:
    """Admite seguridad en 0–1 o 0–100. Devuelve 0–100."""
    try:
        s = float(seg)
    except Exception:
        return 0.0
    if 0.0 <= s <= 1.0:
        return s * 100.0
    return _clamp(s, 0.0, 100.0)

def _norm_bad(x: float, lo: float, hi: float) -> float:
    """
    Normaliza a [0,1] donde lo=bueno(0) y hi=malo(1).
    Clampea si está fuera del rango.
    """
    if hi == lo:
        return 0.0
    return _clamp((x - lo) / (hi - lo), 0.0, 1.0)

def _temp_discomfort(t: float) -> float:
    """
    0 dentro de la zona de confort [22,26]; aumenta hacia [15,35] hasta 1.0.
    Penaliza simétricamente frío/calor respecto al rango óptimo.
    """
    t_lo, t_hi = TEMP_COMFORT
    t_min, t_max = TEMP_MINMAX
    if t < t_lo:
        return _clamp((t_lo - t) / max(t_lo - t_min, 1e-9), 0.0, 1.0)
    if t > t_hi:
        return _clamp((t - t_hi) / max(t_max - t_hi, 1e-9), 0.0, 1.0)
    return 0.0


# -------------------------------
# API escalar (compatibilidad)
# -------------------------------
def calcular_iac(co2: float, ruido: float, temp: float, seguridad: float) -> float:
    """
    Devuelve IAC (0–100, mayor = mejor) para una sola observación.
    """
    co2_n   = _norm_bad(float(co2), *CO2_RANGE)     # 0 bueno, 1 malo
    ruido_n = _norm_bad(float(ruido), *RUIDO_RANGE) # 0 bueno, 1 malo
    temp_n  = _temp_discomfort(float(temp))         # 0 bueno, 1 malo

    seg_0100 = _seg_to_0_100(seguridad)
    seg_n = 1.0 - (seg_0100 / 100.0)                # 0 malo (inseguro), 1 bueno (seguro)

    wsum = w1 + w2 + w3 + w4
    salud = (
        w1 * (1.0 - co2_n) +
        w2 * (1.0 - ruido_n) +
        w3 * (1.0 - temp_n) +
        w4 * (      seg_n)
    ) / wsum

    return round(100.0 * salud, 2)

def calcular_impacto(iac: float, seguridad: float) -> float:
    """
    Impacto (0–100, mayor = peor) combinando bajo IAC + inseguridad.
    Acepta iac en 0–1 o 0–100 y seguridad en 0–1 o 0–100.
    """
    iac_0100 = float(iac) * 100.0 if 0.0 <= float(iac) <= 1.0 else float(iac)
    iac_0100 = _clamp(iac_0100, 0.0, 100.0)

    seg_0100 = _seg_to_0_100(seguridad)
    seg_n = 1.0 - (seg_0100 / 100.0)  # 0=seguro, 1=inseguro

    impacto = 100.0 * (ALPHA_IAC * (1.0 - iac_0100 / 100.0) + ALPHA_SEG * seg_n)
    return round(impacto, 2)


# -------------------------------
# API vectorizada (DataFrame)
# -------------------------------
def _ensure_required_columns(df: pd.DataFrame, cols: Iterable[str] = EXPECTED_INPUT_COLS) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}. "
                         f"Esperadas: {list(cols)}")

def calcular_iac_impacto_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula columnas derivadas para todas las filas del DataFrame:
    - Entradas requeridas: co2, ruido, temperatura, seguridad (0–1 o 0–100)
    - Salidas: iac, impacto, co2_n, ruido_n, temp_n, seg_n
    """
    _ensure_required_columns(df)
    out = df.copy()

    # Normalizaciones "malas": 0=bueno, 1=malo
    out["co2_n"]   = ((out["co2"].astype(float)   - CO2_RANGE[0]) / (CO2_RANGE[1] - CO2_RANGE[0])).clip(0, 1)
    out["ruido_n"] = ((out["ruido"].astype(float) - RUIDO_RANGE[0]) / (RUIDO_RANGE[1] - RUIDO_RANGE[0])).clip(0, 1)

    t = out["temperatura"].astype(float)
    t_lo, t_hi = TEMP_COMFORT
    t_min, t_max = TEMP_MINMAX
    temp_n = np.where(t < t_lo, (t_lo - t) / max(t_lo - t_min, 1e-9), 0.0)
    temp_n = np.where(t > t_hi, (t - t_hi) / max(t_max - t_hi, 1e-9), temp_n)
    out["temp_n"] = np.clip(temp_n, 0, 1)

    seg0100 = out["seguridad"].apply(_seg_to_0_100)
    out["seg_n"] = 1.0 - (seg0100 / 100.0)

    # IAC 0–100 (mayor = mejor)
    wsum = w1 + w2 + w3 + w4
    salud = (
        w1 * (1.0 - out["co2_n"]) +
        w2 * (1.0 - out["ruido_n"]) +
        w3 * (1.0 - out["temp_n"]) +
        w4 * (1.0 - out["seg_n"])   # = seguridad como "bueno"
    ) / wsum
    out["iac"] = (100.0 * salud).round(2)

    # Impacto 0–100 (mayor = peor)
    out["impacto"] = (100.0 * (ALPHA_IAC * (1.0 - out["iac"] / 100.0) + ALPHA_SEG * out["seg_n"])).round(2)

    return out


# -------------------------------
# Simulador por deltas
# -------------------------------
def aplicar_simulador(
    df: pd.DataFrame,
    d_co2: float = 0.0,
    d_temp: float = 0.0,
    d_ruido: float = 0.0,
    d_seg: float = 0.0,
    clip_ranges: bool = True,
) -> pd.DataFrame:
    """
    Aplica deltas globales a las entradas y recalcula IAC/Impacto.
    - d_seg se interpreta en puntos de seguridad 0–100 (no en 0–1).
    - Si clip_ranges=True, se recortan a rangos razonables para evitar outliers.
    """
    _ensure_required_columns(df)
    mod = df.copy()

    # Aplica deltas
    mod["co2"]         = mod["co2"].astype(float) + d_co2
    mod["temperatura"] = mod["temperatura"].astype(float) + d_temp
    mod["ruido"]       = mod["ruido"].astype(float) + d_ruido

    seg0100 = mod["seguridad"].apply(_seg_to_0_100) + d_seg
    mod["seguridad"]   = seg0100

    if clip_ranges:
        mod["co2"]         = mod["co2"].clip(300, 2000)
        mod["temperatura"] = mod["temperatura"].clip(10, 45)
        mod["ruido"]       = mod["ruido"].clip(30, 110)
        mod["seguridad"]   = mod["seguridad"].clip(0, 100)

    # Recalcular métricas derivadas
    return calcular_iac_impacto_df(mod)



