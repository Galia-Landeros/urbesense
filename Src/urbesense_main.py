# urbesense_main.py
# Streamlit app (plug & play) para integrar dataset.csv con limpieza, validación y controles.
# Ejecuta: streamlit run urbesense_main.py

import os
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ==========================
# Configuración / Parámetros
# ==========================

# Umbrales por defecto (ajustables en la UI)
DEFAULTS = {
    "iac_inactiva": 0.35,
    "ruido_alto": 70.0,       # dB
    "co2_alto": 900.0,        # ppm (tu dataset está 20-60; mantengo este como genérico)
    "temp_alta": 32.0,        # °C
}

# Límites (para limpieza/validación) según tu lógica de scripts
LIMITES = {
    "CO2": (20, 60),
    "ruido": (30, 70),
    "IAC": (0.2, 1.0),
    "temperatura": (15, 35),
    "seguridad": (0.2, 1.0),
    "impacto": (0, 100),
}

# Mapeo de columnas del CSV a nombres estandarizados internos
COLUMN_MAP = {
    "zona": "nombre",
    # Mantengo el resto igual
    "CO2": "co2",
    "ruido": "ruido",
    "IAC": "iac",
    "temperatura": "temperatura",
    "seguridad": "seguridad",
    "impacto": "impacto",
    "nivel de impacto": "nivel_impacto",
}

CATEGORIAS_IMPACTO_ORDEN = ["Muy bajo", "Bajo", "Moderado", "Alto", "Muy alto"]

# ==========================
# Utilidades de datos
# ==========================

def apply_column_map(df: pd.DataFrame, colmap: Dict[str, str]) -> pd.DataFrame:
    intersect = {k: v for k, v in colmap.items() if k in df.columns}
    return df.rename(columns=intersect)

def drop_full_na_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(axis=1, how="all")

def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.dropna()  # si luego quieres imputar en lugar de dropear, cámbialo aquí
    for col, (min_val, max_val) in LIMITES.items():
        if col in df.columns:
            df = df[(df[col] >= min_val) & (df[col] <= max_val)]
    return df

def validar_rangos(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un resumen de validación por columna"""
    registros = []
    for col, (minimo, maximo) in LIMITES.items():
        if col in df.columns:
            fuera = df[(df[col] < minimo) | (df[col] > maximo)]
            registros.append({
                "columna": col,
                "min": minimo,
                "max": maximo,
                "fuera_de_rango": len(fuera),
                "total": len(df),
            })
    return pd.DataFrame(registros)

def clasificar_impacto(valor: float) -> str:
    if pd.isna(valor):
        return "Desconocido"
    if valor < 20:
        return "Muy bajo"
    elif valor < 40:
        return "Bajo"
    elif valor < 60:
        return "Moderado"
    elif valor < 80:
        return "Alto"
    else:
        return "Muy alto"

def asegurar_nivel_impacto(df: pd.DataFrame) -> pd.DataFrame:
    # Si no trae nivel_impacto, lo calculamos con la regla dada
    if "nivel_impacto" not in df.columns:
        df["nivel_impacto"] = df["impacto"].apply(clasificar_impacto)
    return df

def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = drop_full_na_columns(df)
    df = apply_column_map(df, COLUMN_MAP)
    # Asegurar tipos numéricos en métricas
    for c in ["co2", "ruido", "iac", "temperatura", "seguridad", "impacto"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Limpieza con límites
    df = limpiar_datos(df)
    # Asegurar nivel impacto
    df = asegurar_nivel_impacto(df)
    # Ordenar columnas para visual
    cols_order = ["nombre", "iac", "seguridad", "impacto", "nivel_impacto", "co2", "ruido", "temperatura"]
    ordered = [c for c in cols_order if c in df.columns] + [c for c in df.columns if c not in cols_order]
    df = df[ordered]
    return df.reset_index(drop=True)

# ==========================
# UI (Streamlit)
# ==========================

st.set_page_config(page_title="UrbeSense – Integración CSV", layout="wide")

st.title("UrbeSense – Integración de dataset y parámetros")

with st.sidebar:
    st.header("Datos")
    uploaded = st.file_uploader("Sube dataset.csv", type=["csv"])
    default_path = st.text_input("o indica ruta local", value="dataset.csv")
    st.caption("Sugerencia: coloca dataset.csv en el mismo directorio del script.")

    st.header("Parámetros (semana)")
    iac_inactiva = st.slider("Umbral IAC inactiva", 0.0, 1.0, float(DEFAULTS["iac_inactiva"]), 0.01)
    ruido_alto = st.number_input("Ruido alto (dB)", value=float(DEFAULTS["ruido_alto"]), step=1.0)
    co2_alto = st.number_input("CO₂ alto (ppm)", value=float(DEFAULTS["co2_alto"]), step=50.0)
    temp_alta = st.number_input("Temperatura alta (°C)", value=float(DEFAULTS["temp_alta"]), step=0.5)

# Carga de datos (uploader > ruta)
df = None
origin = None

if uploaded is not None:
    tmp_path = f".cache/{uploaded.name}"
    Path(".cache").mkdir(exist_ok=True, parents=True)
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    df = load_dataset(tmp_path)
    origin = "uploader"
elif Path(default_path).exists():
    df = load_dataset(default_path)
    origin = default_path

if df is None or df.empty:
    st.info("Sube un CSV o indica una ruta válida para comenzar. Formato esperado: zona, CO2, ruido, IAC, temperatura, seguridad, impacto, nivel de impacto.")
    st.stop()

st.success(f"Dataset cargado desde: {origin if origin else 'desconocido'}")

# Flags y métricas derivadas
df["inactiva"] = df["iac"] < iac_inactiva
df["ruido_alto_flag"] = df["ruido"] > ruido_alto if "ruido" in df.columns else False
df["co2_alto_flag"] = df["co2"] > co2_alto if "co2" in df.columns else False
df["temp_alta_flag"] = df["temperatura"] > temp_alta if "temperatura" in df.columns else False

# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Zonas", df["nombre"].nunique() if "nombre" in df.columns else len(df))
with c2:
    st.metric("Inactivas (<IAC)", int(df["inactiva"].sum()))
with c3:
    if "impacto" in df.columns:
        st.metric("Impacto medio", f"{df['impacto'].mean():.1f}")
    else:
        st.metric("Impacto medio", "—")
with c4:
    if "nivel_impacto" in df.columns:
        counts = df["nivel_impacto"].value_counts()
        top_cat = counts.idxmax()
        st.metric("Nivel de impacto más común", f"{top_cat} ({counts.max()})")
    else:
        st.metric("Nivel de impacto más común", "—")

st.subheader("Vista de datos")
st.dataframe(df, use_container_width=True)

# Validación (similar a validardataset.py)
st.subheader("Validación de rangos")
val = validar_rangos(df.rename(columns={"co2": "CO2"}))  # la validación original usa 'CO2' mayúscula
st.dataframe(val, use_container_width=True)

# Gráficas
charts = st.tabs(["Impacto vs Zona", "IAC vs Seguridad", "Distribución por Nivel de Impacto"])

with charts[0]:
    if {"nombre", "impacto"}.issubset(df.columns):
        fig = px.bar(df, x="nombre", y="impacto", title="Impacto por zona")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Faltan columnas para esta gráfica.")

with charts[1]:
    if {"iac", "seguridad"}.issubset(df.columns):
        fig = px.scatter(df, x="seguridad", y="iac",
                         hover_data=["nombre"] if "nombre" in df.columns else None,
                         title="Relación IAC vs Seguridad")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Faltan columnas para esta gráfica.")

with charts[2]:
    if "nivel_impacto" in df.columns:
        # Asegurar orden consistente
        cat_type = pd.CategoricalDtype(categories=CATEGORIAS_IMPACTO_ORDEN, ordered=True)
        serie = df["nivel_impacto"].astype(cat_type)
        counts = serie.value_counts().reindex(CATEGORIAS_IMPACTO_ORDEN, fill_value=0).reset_index()
        counts.columns = ["nivel_impacto", "cantidad"]
        fig = px.pie(counts, names="nivel_impacto", values="cantidad", title="Distribución por nivel de impacto")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Falta columna 'nivel de impacto'.")

# Export opcional del dataset procesado
st.subheader("Exportar")
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("Descargar CSV procesado", data=csv_bytes, file_name="dataset_procesado.csv", mime="text/csv")

st.caption("Tip: guarda tus umbrales preferidos en un JSON y cárgalos al inicio si quieres persistencia entre sesiones.")
