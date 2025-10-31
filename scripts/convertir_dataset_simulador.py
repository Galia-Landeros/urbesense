# scripts/convertir_dataset_simulador.py
"""
Convierte el archivo 'data/dataset_simulador.csv' o 'dataset_simulacion.csv'
para escalar la columna 'seguridad' de 0–1 a 0–100 si es necesario.

Salida: 'data/dataset_simulador_ajustado.csv'
"""

import pandas as pd
from pathlib import Path

# --- Rutas
DATA_DIR = Path("data")
input_candidates = [
    DATA_DIR / "dataset_simulador.csv",
    DATA_DIR / "dataset_simulacion.csv",
]

# Buscar cuál existe
for p in input_candidates:
    if p.exists():
        csv_path = p
        break
else:
    raise FileNotFoundError("No se encontró ningún dataset_simulador(.csv) o dataset_simulacion(.csv) en /data")

# --- Cargar dataset
df = pd.read_csv(csv_path)
print(f"Archivo leído: {csv_path.name}  |  {len(df)} filas")

# Normalizar nombres de columnas
df.columns = [c.strip().lower() for c in df.columns]

# Verificar columna de seguridad
if "seguridad" not in df.columns:
    raise ValueError("No se encontró la columna 'seguridad' en el CSV.")

# Detectar rango de seguridad actual
seg = df["seguridad"].astype(float)
seg_min, seg_max = seg.min(), seg.max()

if seg_max <= 1.0:
    print(f"Detectado rango 0–1 (min={seg_min:.2f}, max={seg_max:.2f}) → se escalará a 0–100.")
    df["seguridad"] = (df["seguridad"] * 100).round(2)
else:
    print(f"Rango ya está en 0–100 (min={seg_min:.1f}, max={seg_max:.1f}) → no se modifica.")

# Exportar CSV ajustado
out_path = DATA_DIR / "dataset_simulador_ajustado.csv"
df.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"\n✅ Archivo convertido guardado en: {out_path}")
print(df.head())
