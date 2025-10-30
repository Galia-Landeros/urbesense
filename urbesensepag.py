# para que 'src' se importe siempre
import sys
from pathlib import Path
from datetime import datetime

# Asegurar que el root del proyecto esté en sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Imports
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Backend imports
from src.config import DEFAULT_CSV
from src.data_loader import load_dataset
from src.plot_layer import build_map_plotly
from src.utils import file_signature

def file_signature(path: str | Path):
    p = Path(path)
    if not p.exists():
        return None
    s = p.stat()
    return (int(s.st_mtime), int(s.st_size))

# Botón manual de refresco 
if st.sidebar.button("🔄 Actualizar datos"):
    st.cache_data.clear()

# FUNCIÓN CACHED que DEPENDE de la firma del archivo
@st.cache_data
def get_data(csv_path: str, sig):
    return load_dataset(csv_path)

# DEFINE LA RUTA Y LA FIRMA ANTES DE LLAMAR get_data
csv_path = str(DEFAULT_CSV)
sig = file_signature(csv_path)
# CARGA EL DATAFRAME
df = get_data(csv_path, sig)

def _coerce_numeric(df, cols):
    d = df.copy()
    for c in cols:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

st.set_page_config(layout="wide", page_title="Urbesense", page_icon="🏙️")

# =================== ESTILOS UI (CSS) MEJORADO ===================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap');
    
    /* Fondo principal mejorado */
    .main {
        background: linear-gradient(135deg, #8B8FAD 0%, #9A9DB9 50%, #7C7FA0 100%) !important;
        background-attachment: fixed;
    }
    
    .block-container {
        background: transparent !important;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Título Principal Mejorado */
    .titulo-urbesense {
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #005B96 0%, #0081C9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: -0.5px;
        display: inline-block; 
        vertical-align: middle;
    }

    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 2rem 0;
    }

    .header-container img {
        margin: 0;
        display: block;
    }
    
    /* Barra de pestañas premium */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px 12px 0 0;
        margin: 0 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        white-space: pre-wrap;
        background: transparent;
        border-radius: 8px 8px 0 0;
        gap: 8px;
        padding: 12px 24px;
        color: #E2E8F0 !important;
        font-weight: 600;
        font-size: 15px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        font-family: 'Roboto', sans-serif;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.08);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        backdrop-filter: blur(10px);
    }

    /* Tarjetas de métricas premium */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        text-align: center;
        font-family: 'Roboto', sans-serif;
        border: 1px solid rgba(255,255,255,0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #005B96, #0081C9);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }
    
    .metric-value { 
        font-size: 2.5rem; 
        font-weight: 700; 
        color: #1A202C; 
        font-family: 'Roboto', sans-serif;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #1A202C 0%, #2D3748 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label { 
        font-size: 0.9rem; 
        color: #718096; 
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Estilo aplicado directamente a columnas con gráficos */
    [data-testid="column"] > .element-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.8);
        margin-bottom: 1.5rem;
    }

    /* Eliminar espacios entre elementos */
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }

    .stPlotlyChart, .stAltairChart {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    .stMarkdown h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-family: 'Roboto', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #2D3748;
    }
    
    /* Efectos de glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #005B96, #0081C9);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #0081C9, #005B96);
    }
</style>
""", unsafe_allow_html=True)

# =================== TÍTULO CON IMAGEN ===================
col_header = st.columns([1])[0] 
with col_header:
    st.markdown(f"""
    <div class="header-container">
        <img src="https://i.ibb.co/Kjdb3t55/logo1.jpg" width="150" style="vertical-align: middle;">
        <div class="titulo-urbesense">Urbesense</div>
    </div>
    """, unsafe_allow_html=True)

# =================== PESTAÑAS ===================
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard Principal", "🔍 Análisis de Causas", "📊 Simulación Avanzada"])

# =================== CARGA DE DATOS ===================
@st.cache_data
def get_data(path: str) -> pd.DataFrame:
    df = load_dataset(path)
    df = _coerce_numeric(df, ["lat","lon","iac","ruido","co2","temperatura"])
    if "nombre" not in df.columns and "zona" in df.columns:
        df = df.rename(columns={"zona":"nombre"})
    return df

df = get_data(str(DEFAULT_CSV))

# KPIs
n_zonas = len(df) if len(df) else 0
iac_prom = f"{df['iac'].mean():.0f}%" if "iac" in df and len(df) else "—"
areas_olvidadas = int((df["iac"]<40).sum()) if "iac" in df and len(df) else 0
simulaciones = 42

# =================== CONTENIDO DE PESTAÑAS ===================
with tab1:
    # MÉTRICAS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Zonas Analizadas</div>
            <div class="metric-value">{n_zonas}</div>
            <div style="font-size: 0.8rem; color: #48BB78;">✓ Monitoreo activo</div>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Índice de Actividad</div>
            <div class="metric-value">{iac_prom}</div>
            <div style="font-size: 0.8rem; color: #4299E1;">↗️ Tendencia positiva</div>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Áreas Prioritarias</div>
            <div class="metric-value">{areas_olvidadas}</div>
            <div style="font-size: 0.8rem; color: #ED8936;">⚠️ Necesitan atención</div>
        </div>
        ''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Simulaciones</div>
            <div class="metric-value">{simulaciones}</div>
            <div style="font-size: 0.8rem; color: #9F7AEA;">🔮 Proyecciones</div>
        </div>
        ''', unsafe_allow_html=True)

    # GRÁFICOS PRINCIPALES
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🗺️ Actividad por Zona")
        if len(df):
            try:
                fig = build_map_plotly(df)
                st.plotly_chart(fig, use_container_width=True, key="mapa_principal")
            except Exception as e:
                st.error(f"Error al cargar el mapa: {str(e)}")
        else:
            st.info("No hay datos para mostrar en el mapa.")

    with col2:
        st.markdown("### 🏆 Zonas más Seguras")
        if {"nombre", "iac"}.issubset(df.columns):
            top = (df.groupby("nombre", as_index=False)["iac"].mean()
                     .sort_values("iac", ascending=False).head(5))
            chart = alt.Chart(top).mark_bar(cornerRadius=6).encode(
                x=alt.X('nombre:N', sort='-y', title="Zona", axis=alt.Axis(labelAngle=0)),
                y=alt.Y('iac:Q', title="IAC Promedio"),
                color=alt.Color('nombre:N', legend=None, 
                              scale=alt.Scale(scheme='blues'))
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar las zonas más seguras.")

    # GRÁFICOS SECUNDARIOS
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 📅 Evolución Temporal")
        if "fecha" in df.columns and len(df):
            dft = df.copy()
            dft["fecha"] = pd.to_datetime(dft["fecha"], errors="coerce")
            serie = (dft.dropna(subset=["fecha"])
                        .groupby(dft["fecha"].dt.to_period("M"))["iac"].mean()
                        .reset_index())
            serie["fecha"] = serie["fecha"].astype(str)
            line = alt.Chart(serie).mark_line(strokeWidth=3, point=True).encode(
                x=alt.X('fecha:N', title="Mes"),
                y=alt.Y('iac:Q', title="IAC promedio"),
                color=alt.value('#4299E1')
            ).properties(height=300)
            st.altair_chart(line, use_container_width=True)
        else:
            st.info("No hay datos temporales disponibles.")

    with col4:
        st.markdown("### 🎯 Zonas de Alto Riesgo")
        if {"nombre","iac"}.issubset(df.columns) and len(df):
            risky = (df.assign(riesgo=(df["iac"]<40).astype(int))
                       .groupby("nombre", as_index=False)["riesgo"].sum()
                       .sort_values("riesgo", ascending=False).head(5)
                       .rename(columns={"nombre":"Zona","riesgo":"Casos"}))
            pie = alt.Chart(risky).mark_arc(innerRadius=80, stroke="#fff").encode(
                theta='Casos:Q',
                color=alt.Color('Zona:N', scale=alt.Scale(scheme='reds')),
                tooltip=['Zona','Casos']
            ).properties(height=300)
            st.altair_chart(pie, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar zonas de riesgo.")

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🔍 Análisis de Causas")
    st.markdown("""
    <div style='text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%); border-radius: 12px; border: 2px dashed #CBD5E0;'>
        <h3 style='color: #4A5568; margin-bottom: 1rem;'>🚀 Área de Análisis Avanzado</h3>
        <p style='color: #718096; font-size: 1.1rem; line-height: 1.6;'>
            Esta sección está diseñada para análisis profundos de factores causales.<br>
            Espacio preparado para implementar modelos predictivos y análisis estadísticos avanzados.
        </p>
        <div style='margin-top: 2rem; padding: 1.5rem; background: white; border-radius: 8px;'>
            <h4 style='color: #2D3748;'>📋 Próximas Implementaciones</h4>
            <ul style='text-align: left; color: #718096;'>
                <li>Análisis de correlación multivariada</li>
                <li>Modelos de machine learning predictivo</li>
                <li>Análisis de series temporales</li>
                <li>Dashboards de diagnóstico causal</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Simulación Avanzada")
    if len(df):
        try:
            fig = build_map_plotly(df)
            st.plotly_chart(fig, use_container_width=True, key="mapa_simulacion")
        except Exception as e:
            st.error(f"Error al cargar el mapa de simulación: {str(e)}")
    else:
        st.info("No hay datos para mostrar en el mapa.")
    st.markdown('</div>', unsafe_allow_html=True)

# =================== FOOTER ===================
st.markdown("""
<div style='text-align: center; margin-top: 4rem; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 12px;'>
    <p style='color: #E2E8F0; font-size: 0.9rem; margin: 0;'>
        🏙️ Urbesense Analytics Platform • Monitoreo Inteligente de Espacios Urbanos 
        <br>
        <span style='color: #CBD5E0; font-size: 0.8rem;'>
            Última actualización: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
        </span>
    </p>
</div>
""", unsafe_allow_html=True)