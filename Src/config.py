"""Configuración general y parámetros de visualización (Semana 1)."""
"""Configuración general y parámetros de visualización."""
from pathlib import Path
import os

# Rutas base
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR     = PROJECT_ROOT / "data"

# CSV de entrada (SEED) — valores crudos SIN iac/impacto
SEED_CSV     = DATA_DIR / "zona.csv"

# Compatibilidad con código viejo que esperaba DEFAULT_CSV
DEFAULT_CSV  = SEED_CSV

# Esquemas esperados
EXPECTED_SEED = [
    "zona_id", "nombre", "lat", "lon",
    "co2", "ruido", "temperatura", "seguridad",
]

# Si en algún momento decides persistir métricas (opcional):
EXPECTED_METRICS = EXPECTED_SEED + [
    "iac", "impacto",           # salidas
    # opcionales si las guardas
    "co2_n", "ruido_n", "temp_n", "seg_n",
]

# Clasificación IAC (0–100)
# <40 bajo, 40–69 medio, >=70 alto
IAC_THRESHOLDS = {"high": 70, "mid": 40}

# Estilo Plotly
PLOTLY_TEMPLATE = "plotly_white"

# Token de Mapbox (usa variable de entorno si existe)
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", None)

# (Opcional) límites geográficos recomendados para Campeche
AOI_LAT = (19.80, 19.90)
AOI_LON = (-90.60, -90.48)
