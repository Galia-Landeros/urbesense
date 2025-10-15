import streamlit as st
import pydeck as pdk
import pandas as pd

# Cargar datos
df = pd.read_csv("data_zonas.csv")

# Eliminar espacios en nombres de columnas
df.columns = df.columns.str.strip()

# Calcular IAC
df["IAC"] = (
    0.4 * df["co2"] / df["co2"].max() +
    0.3 * df["ruido"] / df["ruido"].max() +
    0.3 * df["movimiento"] / df["movimiento"].max()
)

# Asignar coordenadas (ejemplo)
df["lat"] = [19.845, 19.850, 19.853]
df["lon"] = [-90.528, -90.520, -90.523]

# Clasificar zonas por color
def get_color_name(iac):
    if iac > 0.7:
        return "red"
    elif iac > 0.4:
        return "yellow"
    else:
        return "blue"

df["color"] = df["IAC"].apply(get_color_name)

# Convertir colores a RGB
def get_rgb(color):
    if color == "red":
        return [255, 0, 0, 160]
    elif color == "yellow":
        return [255, 255, 0, 160]
    else:
        return [0, 0, 255, 160]

df["rgb"] = df["color"].apply(get_rgb)

# Crear capa de PyDeck
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_color='rgb',
    get_radius=100,
    pickable=True,
)

# Mostrar mapa
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
