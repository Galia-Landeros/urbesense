# main/app.py
import streamlit as st
import numpy as np
from pathlib import Path

from src.data_loader import load_zonas_csv
from src.calculariac import calcular_iac_impacto_df
from src.plot_layer import bubble_map

# opcional: captura de clics
try:
    from streamlit_plotly_events import plotly_events
    HAS_CLICK = True
except Exception:
    HAS_CLICK = False

st.set_page_config(page_title="UrbeSense • Impacto", layout="wide")
st.title("UrbeSense • Simulador por zona")

# estado
if "zona_sel" not in st.session_state:
    st.session_state["zona_sel"] = None

# datos base
df_raw  = load_zonas_csv("data/zona.csv")
df_calc = calcular_iac_impacto_df(df_raw)

col_map, col_side = st.columns([2,1], gap="large")

with col_map:
    st.subheader("Mapa interactivo")
    fig = bubble_map(df_calc, color_field="impacto")

    clicked_name = None
    if HAS_CLICK:
        click = plotly_events(fig, click_event=True, hover_event=False, select_event=False, key="mapa")
        if click:
            cd = click[0].get("customdata", None)
            if isinstance(cd, list) and len(cd) > 0:
                clicked_name = cd[0]
        if clicked_name:
            st.info(f"Zona bajo el cursor: **{clicked_name}**")
            if st.button("🟢 Seleccionar zona", use_container_width=True):
                st.session_state["zona_sel"] = clicked_name
                st.experimental_rerun()
    else:
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Tip: instala `streamlit-plotly-events` para seleccionar con clic.")

with col_side:
    st.subheader("Zona seleccionada")

    # opción 1: lista (siempre disponible)
    zonas = df_calc["nombre"].tolist()
    manual = st.selectbox("Elegir zona (manual)", ["(ninguna)"] + zonas, index=0)
    if manual != "(ninguna)":
        st.session_state["zona_sel"] = manual

    zona_sel = st.session_state["zona_sel"]
    if not zona_sel:
        st.caption("Selecciona una zona en la lista o haz clic en el mapa y pulsa **Seleccionar zona**.")
        st.stop()

    # sliders por zona (afectan SOLO la zona elegida)
    st.success(f"Zona seleccionada: **{zona_sel}**")
    row = df_calc[df_calc["nombre"] == zona_sel].iloc[0]
    st.write(f"Base → CO₂: {int(row.co2)} ppm • Ruido: {int(row.ruido)} dB • Temp: {row.temperatura:.1f} °C • Seg: {int(row.seguridad)}")
    st.markdown("---")

    d_co2  = st.slider("Δ CO₂ (ppm)", -300, 300, 0, 10, key="dco2")
    d_temp = st.slider("Δ Temperatura (°C)", -10, 10, 0, 1, key="dtemp")
    d_ruido= st.slider("Δ Ruido (dB)", -20, 20, 0, 1, key="druido")
    d_seg  = st.slider("Δ Seguridad (pts)", -30, 30, 0, 1, key="dseg")

# aplicar deltas a UNA sola zona y recalcular
df_sim = df_calc.copy()
mask = df_sim["nombre"] == st.session_state["zona_sel"]
df_sim.loc[mask, "co2"]         = (df_sim.loc[mask, "co2"] + d_co2).clip(300, 2000)
df_sim.loc[mask, "temperatura"] = (df_sim.loc[mask, "temperatura"] + d_temp).clip(10, 45)
df_sim.loc[mask, "ruido"]       = (df_sim.loc[mask, "ruido"] + d_ruido).clip(30, 110)
df_sim.loc[mask, "seguridad"]   = (df_sim.loc[mask, "seguridad"] + d_seg).clip(0, 100)

from src.calculariac import calcular_iac_impacto_df as _recalc
df_sim = _recalc(df_sim)

# re-render mapa actualizado (y resaltamos la zona seleccionada)
with col_map:
    fig2 = bubble_map(df_sim, color_field="impacto")
    # boost visual a la zona seleccionada
    size = np.interp(df_sim["impacto"].to_numpy(float), [0,100], [10,40])
    size *= np.where(df_sim["nombre"] == st.session_state["zona_sel"], 1.3, 1.0)
    for tr in fig2.data:
        if hasattr(tr, "marker") and hasattr(tr.marker, "size"):
            tr.marker.size = size.tolist()
    st.plotly_chart(fig2, use_container_width=True)

with col_side:
    st.subheader("Indicadores")
    st.metric("IAC promedio", f"{df_sim['iac'].mean():.1f}")
    st.metric("Impacto promedio", f"{df_sim['impacto'].mean():.1f}")
    st.dataframe(
        df_sim[["nombre","iac","impacto","co2","ruido","temperatura","seguridad"]]
            .sort_values("impacto", ascending=False),
        use_container_width=True, height=340
    )
