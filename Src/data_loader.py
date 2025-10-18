
# ...existing code...
import pandas as pd
from pathlib import Path
from .config import EXPECTED_COLUMNS

def load_dataset(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {path}")

    df = pd.read_csv(path)

    # Allow EXPECTED_COLUMNS to be a comma-separated string or a list
    if isinstance(EXPECTED_COLUMNS, str):
        expected = [c.strip() for c in EXPECTED_COLUMNS.split(",")]
    else:
        expected = list(EXPECTED_COLUMNS)

    # Common aliases mapping from provided CSV to expected names
    aliases = {
        "zona": "nombre",
        "zona_id": "zona_id",
        "movimiento": "iac",
        "iac": "iac",
        "co2": "co2",
        "ruido": "ruido",
        "temperatura": "temperatura",
    }

    # Apply alias mapping when possible
    for src_col, target_col in aliases.items():
        if src_col in df.columns and target_col not in df.columns:
            df[target_col] = df[src_col]

    # Check missing columns
    missing = [c for c in expected if c not in df.columns]
    if missing:
        # Fill common missing columns with safe defaults so UI can run.
        # Adjust behavior here if you prefer to raise instead.
        for c in missing:
            if c in ("lat", "lon"):
                df[c] = 0.0
            elif c in ("fecha",):
                df[c] = pd.to_datetime("1970-01-01")
            elif c in ("hora",):
                df[c] = "00:00"
            else:
                df[c] = pd.NA
        print(f"WARNING: columnas faltantes rellenadas con valores por defecto: {missing}")

    return df
# ...existing code...