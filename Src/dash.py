from pathlib import Path 
import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import sys

st.markdown("## 🌍 Diagnóstico ambiental inicial")
st.title("URBANSENSE")
st.write("Visualización y simulacion del Índice de Actividad Ciudadana (IAC)")

#Cargar datos
base = Path(__file__).resolve().parent.parent
csv_path = base /"data" / "dataprueba.csv"

print("resolved csv path:", csv_path)
if not csv_path.exists():
    print("file does not exist:", csv_path)
    sys.exit(1)

df = pd.read_csv(csv_path)

#Asignar coordenadas (ejemplo)
df["lat"] = [19.845, 19.850, 19.853]
df["lon"] = [-90.528, -90.520, -90.523]

#selecciona una zona para cambiar c02
zona_sel = st.selectbox("Selecciona una zona para modificar CO₂:", df["zona"])
cambio = st.slider("Aumentar CO₂ de la zona seleccionada (%)", 0, 200, 0)

# Aplica el cambio solo a esa zona
df.loc[df["zona"] == zona_sel, "co2"] *= (1 + cambio / 100)

#Calcula el IAC
df["IAC"] = (
    0.3 * df["co2"] / df["co2"].max() +
    0.3 * df["ruido"] / df["ruido"].max() +
    0.3 * df["movimiento"] / df["movimiento"].max()+
    0.1 * df["temperatura"] / df["temperatura"].max()
)

#Esto da color segun el iac
def get_color(iac):
    if iac > 0.7:
        return "rojo"
    elif iac > 0.4:
        return "amarillo"
    else:
        return "azul"

df["color"] = df["IAC"].apply(get_color)

def get_rgb(color):
    if color == "rojo":
        return [255, 0, 0, 160]
    elif color == "amarillo":
        return [255, 255, 0, 160]
    else:
        return [0, 0, 255, 160]

df["rgb"] = df["color"].apply(get_rgb)

#crear una capa de pydeck
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_color='rgb',
    get_radius=100,
    pickable=True,
)

#mostrar el mapa
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=19.85,
        longitude=-90.52,
        zoom=13,
        pitch=0,
    ),
    layers=[layer],
))

#panel lateral
zona = st.sidebar.selectbox("Selecciona una zona:", df["zona"])
zona_data = df[df["zona"] == zona].iloc[0]

st.sidebar.write(f"CO₂: {zona_data['co2']}")
st.sidebar.write(f"Ruido: {zona_data['ruido']}")
st.sidebar.write(f"Temperatura: {zona_data['temperatura']}")
st.sidebar.write(f"Movimiento: {zona_data['movimiento']}")
st.sidebar.write(f"IAC: {zona_data['IAC']:.2f}")  

#Esto muestra la tabla
st.subheader("Datos procesados")
st.dataframe(df)

#esto muestra el gráfico
st.subheader("Gráfico del IAC por zona")
st.bar_chart(df, x="zona", y="IAC")

