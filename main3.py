# para que 'src' se importe siempre
import sys
from pathlib import Path
from datetime import datetime

# Asegurar que el root del proyecto esté en sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#Imports
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Backend imports
# Backend imports
from src.config import DEFAULT_CSV
from src.data_loader import load_dataset
from src.utils import file_signature
from src.plot_layer import build_map_plotly

#la primera llamada es set_page_config
st.set_page_config(page_title="Urbesense", layout="wide")

def _coerce_numeric(df, cols):
    """Convierte columnas a numéricas sin romper el dataframe."""
    d = df.copy()
    for c in cols:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

# Botón manual de refresco 
if st.sidebar.button("🔄 Actualizar datos"):
    st.cache_data.clear()

# FUNCIÓN CACHED que DEPENDE de la firma del archivo
@st.cache_data
def get_data(csv_path: str, sig):
    # 'sig' solo sirve para invalidar cache, no lo uses adentro.
    return load_dataset(csv_path)

# DEFINE LA RUTA Y LA FIRMA ANTES DE LLAMAR get_data
csv_path = str(DEFAULT_CSV)
sig = file_signature(csv_path)

# CARGA EL DATAFRAME (AHORA SÍ EXISTE df)
df = get_data(csv_path, sig)

# ============= BLOQUE DIAGNÓSTICO (después de cargar df) =============
st.write("Shape tras loader:", df.shape)

# ¿Cuántas filas tienen coordenadas válidas?
if {"lat","lon"}.issubset(df.columns):
    has_coords = df[["lat","lon"]].notna().all(axis=1)
    st.write("Con lat/lon válidos:", int(has_coords.sum()))
else:
    st.write("El dataset no trae lat/lon.")

# Revisa límites que podrían estar filtrando
LIMITES_DEBUG = {
    "co2": (20, 5000),     # mismo criterio adaptativo
    "ruido": (30, 70),
    "iac": (0.2, 1.0),
    "temperatura": (15, 35),
    "seguridad": (0.2, 1.0),
    "impacto": (0, 100),
}
fuera = []
for col, (mn, mx) in LIMITES_DEBUG.items():
    if col in df.columns:
        mask = ~(df[col].between(mn, mx))
        if mask.any():
            fuera.append((col, int(mask.sum()), df.loc[mask, ["nombre", col]].head(10)))
st.write("Valores fuera de rango (muestra):", [(c, n) for c, n, _ in fuera])
for c, n, ej in fuera:
    st.write(f"Ejemplos fuera de {c}:", ej)

# ¿Qué filas van al mapa?
cols_preview = [c for c in ["nombre","lat","lon","iac","co2","ruido","temperatura","seguridad","impacto","nivel_impacto"] if c in df.columns]
st.write("Primeras filas que van al mapa:", df[cols_preview].head())
# =====================================================================

# =================== ESTILOS UI (CSS tal cual) ===================
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .main { padding-top: 0px !important; }
    .block-container { padding-top: 1rem; }
    body { background-color: #F8F9FA; }

    .main-container { display: flex; flex-direction: row; }
    .sidebar {
        background-color: #ffffff; width: 80px; height: 100vh;
        display: flex; flex-direction: column; align-items: center;
        padding-top: 40px; box-shadow: 2px 0 8px rgba(0,0,0,0.05);
        position: fixed; left: 0; top: 0; z-index: 1000;
    }
    .sidebar img {
        width: 28px; height: 28px; margin: 20px 0; opacity: 0.7; cursor: pointer; transition: 0.2s;
    }
    .sidebar img:hover { opacity: 1; transform: scale(1.1); }

    .content { margin-left: 100px; padding: 20px; width: calc(100% - 100px); }
    .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; width: 100%; }
    .title-wrapper { flex-grow: 1; text-align: center; padding-left: 320px; }
    .title { font-size: 62px; font-weight: 700; color: #005B96; }

    .buttons button {
        background-color: #e5e7eb; border: none; color: #111827; padding: 8px 16px;
        border-radius: 8px; font-weight: 600; margin-right: 10px; transition: background-color 0.3s ease;
    }
    .buttons button:hover { background-color: #FFA500; cursor: pointer; }

    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05); text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #111827; }
    .metric-label { font-size: 14px; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sidebar">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHVo0hD_bA9XSw-pQrc7p-99aSWJGYHxcQTQ&usqp=CAU" title="Gataso" />
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHVo0hD_bA9XSw-pQrc7p-99aSWJGYHxcQTQ&usqp=CAU" title="Zonas" />
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHVo0hD_bA9XSw-pQrc7p-99aSWJGYHxcQTQ&usqp=CAU" title="Mapas" />
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHVo0hD_bA9XSw-pQrc7p-99aSWJGYHxcQTQ&usqp=CAU" title="Causas" />
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHVo0hD_bA9XSw-pQrc7p-99aSWJGYHxcQTQ&usqp=CAU" title="Configuración" />
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="content">', unsafe_allow_html=True)

# =================== HEADER ===================
st.markdown("""
<div class="header">
    <div class="title-wrapper"><div class="title">Urbesense</div></div>
    <div class="buttons">
        <button>Zonas</button>
        <button>Causas</button>
        <button>Intervenciones</button>
    </div>
</div>
""", unsafe_allow_html=True)

# =================== BACKEND: datos + caché ===================
@st.cache_data
def get_data(path: str) -> pd.DataFrame:
    df = load_dataset(path)
    df = _coerce_numeric(df, ["lat","lon","iac","ruido","co2","temperatura"])
    # Normaliza columnas comunes por si vienen mal tipadas
    if "nombre" not in df.columns and "zona" in df.columns:
        df = df.rename(columns={"zona":"nombre"})
    return df

df = get_data(str(DEFAULT_CSV))

# KPIs reales (si no hay datos, muestra —)
n_zonas = len(df) if len(df) else 0
iac_prom = f"{df['iac'].mean():.0f}%" if "iac" in df and len(df) else "—"
areas_olvidadas = int((df["iac"]<40).sum()) if "iac" in df and len(df) else 0  # regla: IAC<40
simulaciones = 42  # placeholder hasta que agregues módulo simulador

# =================== MÉTRICAS (tu UI) ===================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Zonas Analizadas</div><div class="metric-value">{n_zonas}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Índice de Actividad</div><div class="metric-value">{iac_prom}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Áreas Olvidadas</div><div class="metric-value">{areas_olvidadas}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Simulaciones</div><div class="metric-value">{simulaciones}</div></div>', unsafe_allow_html=True)

st.write("")
col1, col2 = st.columns(2)

# =================== MAPA (Plotly desde tu backend) ===================
with col1:
    st.markdown("### Actividad por Zona")
    if len(df):
        fig = build_map_plotly(df)  # usa src/plot_layer.py (scattermapbox con OSM)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar en el mapa.")

# =================== CAUSAS (si existen columnas; si no, fallback) ===================
with col2:
    st.markdown("### Causas Principales")
    if {"causa","impacto"}.issubset(df.columns):
        top = (df.groupby("causa", as_index=False)["impacto"].mean()
                 .sort_values("impacto", ascending=False).head(5))
        chart = alt.Chart(top).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('causa:N', sort='-y', title="Causa"),
            y=alt.Y('impacto:Q', title="Impacto promedio"),
            color=alt.Color('causa:N', legend=None)
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        df_bar = pd.DataFrame({
            'Causa': ['Falta de iluminación', 'Basura', 'Abandono', 'Inseguridad', 'Contaminación'],
            'Impacto': [80, 65, 60, 55, 40]
        })
        chart = alt.Chart(df_bar).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('Causa', sort='-y'),
            y='Impacto',
            color=alt.Color('Causa', legend=None)
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

st.write("")
col3, col4 = st.columns(2)

# =================== LÍNEA TEMPORAL (si hay fecha) ===================
with col3:
    st.markdown("### Nivel de Intervención por Sector / Tiempo")
    if "fecha" in df.columns and len(df):
        dft = df.copy()
        dft["fecha"] = pd.to_datetime(dft["fecha"], errors="coerce")
        serie = (dft.dropna(subset=["fecha"])
                    .groupby(dft["fecha"].dt.to_period("Y"))["iac"].mean()
                    .reset_index())
        serie["fecha"] = serie["fecha"].astype(str)
        line = alt.Chart(serie).mark_line(point=True).encode(
            x=alt.X('fecha:N', title="Año"),
            y=alt.Y('iac:Q', title="IAC promedio")
        ).properties(height=300)
        st.altair_chart(line, use_container_width=True)
    else:
        df_line = pd.DataFrame({'Año': range(2018, 2026), 'Nivel': np.random.randint(40, 100, 8)})
        line = alt.Chart(df_line).mark_line(point=True).encode(x='Año', y='Nivel').properties(height=300)
        st.altair_chart(line, use_container_width=True)

# =================== PIE DE RIESGO (basado en IAC) ===================
with col4:
    st.markdown("### Zonas con Mayor Riesgo")
    if {"nombre","iac"}.issubset(df.columns) and len(df):
        risky = (df.assign(riesgo=(df["iac"]<40).astype(int))
                   .groupby("nombre", as_index=False)["riesgo"].sum()
                   .sort_values("riesgo", ascending=False).head(5)
                   .rename(columns={"nombre":"Zona","riesgo":"Casos"}))
        total = risky["Casos"].sum()
        risky["Porcentaje"] = (risky["Casos"] / total * 100.0).round(1) if total else 0
        pie = alt.Chart(risky).mark_arc(innerRadius=50).encode(
            theta='Porcentaje:Q',
            color='Zona:N',
            tooltip=['Zona','Casos','Porcentaje']
        ).properties(height=300)
        st.altair_chart(pie, use_container_width=True)
    else:
        df_pie = pd.DataFrame({'Zona': ['Centro', 'Norte', 'Sur', 'Este', 'Oeste'],
                               'Porcentaje': [25, 20, 15, 30, 10]})
        pie = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(theta='Porcentaje', color='Zona')
        st.altair_chart(pie, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
