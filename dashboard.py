import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --------------------------
# CONFIGURACIÓN GENERAL
# --------------------------
st.set_page_config(page_title="Dashboard Urbano", layout="wide")

# --------------------------
# ESTILOS PERSONALIZADOS (HTML + CSS)
# --------------------------
st.markdown("""
<style>
    /* Fondo general */
    body {
        background-color: #F8F9FA;
    }

    /* Contenedor principal */
    .main-container {
        display: flex;
        flex-direction: row;
    }

    /* Barra lateral personalizada */
    .sidebar {
        background-color: #ffffff;
        width: 80px;
        height: 100vh; /* altura completa de la ventana */
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 40px; /* bajamos los iconos un poco más */
        box-shadow: 2px 0 8px rgba(0,0,0,0.05);
        position: fixed;
        left: 0;
        top: 0;
        z-index: 1000;
    }

    .sidebar img {
        width: 28px;
        height: 28px;
        margin: 20px 0;
        opacity: 0.7;
        cursor: pointer;
        transition: 0.2s;
    }

    .sidebar img:hover {
        opacity: 1;
        transform: scale(1.1);
    }

    /* Contenido del dashboard */
    .content {
        margin-left: 100px;
        padding: 20px;
        width: calc(100% - 100px);
    }

    /* Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20px;
    }

    .title {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
    }

    .buttons button {
        background-color: #e5e7eb;
        border: none;
        color: #111827;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-right: 10px;
    }

    .buttons button:hover {
        background-color: #d1d5db;
        cursor: pointer;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }

    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #111827;
    }

    .metric-label {
        font-size: 14px;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# MENÚ LATERAL PERSONALIZADO (ICONOS)
# --------------------------
st.markdown("""
<div class="sidebar">
    <img src="https://cdn-icons-png.flaticon.com/512/1828/1828884.png" title="Dashboard" />
    <img src="https://cdn-icons-png.flaticon.com/512/1041/1041916.png" title="Zonas" />
    <img src="https://cdn-icons-png.flaticon.com/512/1170/1170576.png" title="Mapas" />
    <img src="https://cdn-icons-png.flaticon.com/512/2099/2099058.png" title="Causas" />
    <img src="https://cdn-icons-png.flaticon.com/512/2099/2099199.png" title="Configuración" />
</div>
""", unsafe_allow_html=True)

# --------------------------
# CONTENIDO PRINCIPAL
# --------------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

# Encabezado
st.markdown("""
<div class="header">
    <div class="title">🏙 Dashboard Urbano</div>
    <div class="buttons">
        <button>Zonas</button>
        <button>Causas</button>
        <button>Intervenciones</button>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# TARJETAS DE MÉTRICAS
# --------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card"><div class="metric-label">Zonas Analizadas</div><div class="metric-value">125</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-label">Índice de Actividad</div><div class="metric-value">73%</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-label">Áreas Olvidadas</div><div class="metric-value">18</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><div class="metric-label">Simulaciones</div><div class="metric-value">42</div></div>', unsafe_allow_html=True)

# --------------------------
# PRIMERA FILA DE GRÁFICOS
# --------------------------
st.write("")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Actividad por Zona")
    df = pd.DataFrame(np.random.randn(100, 2) / [50, 50] + [19.43, -99.13], columns=['lat', 'lon'])
    st.map(df, zoom=10)

with col2:
    st.markdown("### Causas Principales")
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

# --------------------------
# SEGUNDA FILA DE GRÁFICOS
# --------------------------
st.write("")
col3, col4 = st.columns(2)

with col3:
    st.markdown("### Nivel de Intervención por Sector")
    df_line = pd.DataFrame({
        'Año': range(2015, 2025),
        'Nivel': np.random.randint(40, 100, 10)
    })
    line = alt.Chart(df_line).mark_line(point=True).encode(x='Año', y='Nivel')
    st.altair_chart(line, use_container_width=True)

with col4:
    st.markdown("### Zonas con Mayor Riesgo")
    df_pie = pd.DataFrame({
        'Zona': ['Centro', 'Norte', 'Sur', 'Este', 'Oeste'],
        'Porcentaje': [25, 20, 15, 30, 10]
    })
    pie = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
        theta='Porcentaje',
        color='Zona'
    )
    st.altair_chart(pie, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

