# src/data_loader.py
import pandas as pd

# === MAPEO Y LÍMITES ===
RENAME_MAP = {
    "zona": "nombre",
    "CO2": "co2",
    "IAC": "iac",
    "nivel de impacto": "nivel_impacto",
    "latitude": "lat",
    "latitud": "lat",
    "longitude": "lon",
    "longitud": "lon",
}

LIMITES = {
    "co2": (20, 60),
    "ruido": (30, 70),
    "iac": (0.2, 1.0),
    "temperatura": (15, 35),
    "seguridad": (0.2, 1.0),
    "impacto": (0, 100),
}

# === FUNCIONES DE APOYO ===
def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia encabezados y renombra columnas."""
    cols = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("\ufeff", "", regex=False)
    )
    df.columns = cols
    df = df.rename(columns=RENAME_MAP)
    return df

def _clasificar_impacto(valor: float) -> str:
    if pd.isna(valor): return "Desconocido"
    if valor < 20:   return "Muy bajo"
    if valor < 40:   return "Bajo"
    if valor < 60:   return "Moderado"
    if valor < 80:   return "Alto"
    return "Muy alto"

# === FUNCIÓN PRINCIPAL ===
def load_dataset(path: str) -> pd.DataFrame:
    """Carga, limpia y valida el dataset principal de UrbeSense."""
    # 1) Leer y normalizar encabezados
    df = pd.read_csv(path, encoding="utf-8")
    df = _normalize_columns(df)


    # 2) Conversión de tipos numéricos
    num_cols = ["co2", "ruido", "iac", "temperatura", "seguridad", "impacto", "lat", "lon"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 3) *** Compatibilidad + límites adaptativos ***
    # 3.1) Normaliza IAC si venía en porcentaje (0–100) a 0–1
    if "iac" in df.columns:
        try:
            if pd.to_numeric(df["iac"], errors="coerce").max(skipna=True) > 1.0:
                df["iac"] = df["iac"] / 100.0
        except Exception:
            pass

    # 3.2) Construye límites locales a partir de LIMITES
    local_limits = LIMITES.copy()

    # 3.3) Ajuste ADAPTATIVO para CO2:
    #      - Si el máximo de CO2 > 100, asumimos ppm ambientales: relajamos SOLO el tope superior,
    #        pero NO subimos el inferior (así no se descartan filas 20–60).
    if "co2" in df.columns:
        co2_num = pd.to_numeric(df["co2"], errors="coerce")
        co2_max = co2_num.max(skipna=True)
        if pd.notna(co2_max) and co2_max > 100:
            local_limits["co2"] = (20, 5000)
    
    # 4) Limpieza básica
    df = df.drop_duplicates()
    df = df.dropna(subset=["nombre"])
    #DIAGNOSTICO 4
    print(f"[DL] After drops: {df.shape}")

    # 5) Cálculo de impacto si no está
    if "impacto" not in df.columns and {"iac", "seguridad"}.issubset(df.columns):
        df["impacto"] = (1 - ((df["iac"] + df["seguridad"]) / 2)) * 100

    # 6) Clasificación de nivel_impacto si no está
    if "nivel_impacto" not in df.columns and "impacto" in df.columns:
        df["nivel_impacto"] = df["impacto"].apply(_clasificar_impacto)
    

    # 7) Validación de límites numéricos (usa local_limits)
    for col, (mn, mx) in local_limits.items():
        if col in df.columns:
            df = df[(df[col] >= mn) & (df[col] <= mx)]
    


    # 8) Validación de coordenadas
    if {"lat", "lon"}.issubset(df.columns):
        df = df.dropna(subset=["lat", "lon"])
        df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]
     

    # 9) Orden recomendado
    order = ["nombre", "iac", "seguridad", "impacto", "nivel_impacto",
             "co2", "ruido", "temperatura", "lat", "lon"]
    df = df[[c for c in order if c in df.columns] + [c for c in df.columns if c not in order]]

    return df.reset_index(drop=True)

