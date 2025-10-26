"""Configuración general y parámetros de visualización (Semana 1)."""
from pathlib import Path

# Rutas base
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_CSV = DATA_DIR / "data_zonas.csv"

# Esquema esperado del CSV
EXPECTED_COLUMNS = [
    "zona_id, nombre, iac, ruido, co2, temperatura, fecha, hora, lat, lon"
]

# Clasificación IAC para color 
IAC_THRESHOLDS = {"high": 70, "mid": 40}  # <40 bajo, 40-69 medio, >=70 alto

# Estilo Plotly 
PLOTLY_TEMPLATE = "plotly_white"

#  MAPBOX TOKEN 
MAPBOX_TOKEN = None  #reemplazar mañana si hace falta