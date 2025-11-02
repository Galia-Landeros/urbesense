# main/app.py
import streamlit as st
from src.data_loader import load_zonas_csv
from src.calculariac import calcular_iac_impacto_df
from src.plot_layer import bubble_map

st.set_page_config(page_title="UrbeSense • Impacto", layout="wide")
st.title("UrbeSense • Mapa de Impacto (Simulador por zona)")

# 1) Cargar datos (USA TU RUTA REAL)
df_raw  = load_zonas_csv("data/zona.csv")  # <-- ojo aquí
df_calc = calcular_iac_impacto_df(df_raw)  # calcula IAC/Impacto

# 2) Sidebar: selector de zona + sliders (FORMATO ORIGINAL)
with st.sidebar:
    st.subheader("Simulador por zona")

    zonas = df_calc["nombre"].tolist()
    zona_sel = st.selectbox("Selecciona una zona", zonas, index=0)

    st.markdown("---")
    st.caption("Ajusta los valores solo para la zona seleccionada:")

    d_co2  = st.slider("Δ CO₂ (ppm)", -300, 300, 0, 10)
    d_temp = st.slider("Δ Temperatura (°C)", -10, 10, 0, 1)
    d_ruido= st.slider("Δ Ruido (dB)", -20, 20, 0, 1)
    d_seg  = st.slider("Δ Seguridad (pts)", -30, 30, 0, 1)

# 3) Aplicar deltas SOLO a esa zona y recalcular
df_sim = df_calc.copy()
mask = (df_sim["nombre"] == zona_sel)
df_sim.loc[mask, "co2"]         = (df_sim.loc[mask, "co2"] + d_co2).clip(300, 2000)
df_sim.loc[mask, "temperatura"] = (df_sim.loc[mask, "temperatura"] + d_temp).clip(10, 45)
df_sim.loc[mask, "ruido"]       = (df_sim.loc[mask, "ruido"] + d_ruido).clip(30, 110)
df_sim.loc[mask, "seguridad"]   = (df_sim.loc[mask, "seguridad"] + d_seg).clip(0, 100)

from src.calculariac import calcular_iac_impacto_df as _recalc
df_sim = _recalc(df_sim)

# 4) Pintar mapa
fig = bubble_map(df_sim, color_field="impacto")
st.plotly_chart(fig, use_container_width=True)

# 5) Tabla y KPIs (opcionales)
col1, col2 = st.columns([1,1])
with col1:
    st.metric("IAC promedio", f"{df_sim['iac'].mean():.1f}")
with col2:
    st.metric("Impacto promedio", f"{df_sim['impacto'].mean():.1f}")

st.dataframe(
    df_sim[["nombre","iac","impacto","co2","ruido","temperatura","seguridad"]]
        .sort_values("impacto", ascending=False),
    use_container_width=True, height=340
)
st.write("Preview datos crudos (zona.csv):")
st.dataframe(df_raw)

st.write("Rango lat:", float(df_raw["lat"].min()), "→", float(df_raw["lat"].max()))
st.write("Rango lon:", float(df_raw["lon"].min()), "→", float(df_raw["lon"].max()))

