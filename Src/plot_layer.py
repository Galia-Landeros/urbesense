# src/plot_layer.py
import numpy as np
import pandas as pd
import plotly.express as px

COLOR_SCALE = [(0.0,"#2ECC71"), (0.5,"#F1C40F"), (1.0,"#E74C3C")]

def bubble_map(df: pd.DataFrame, color_field="impacto",
               center=(19.845, -90.535), zoom=12, opacity=0.6):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("bubble_map espera un pandas.DataFrame")

    # columnas mínimas
    required = {"lat","lon","nombre",color_field}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas para el mapa: {missing}")

    # limpia filas inválidas (si hay NaN no sale nada)
    safe = df.dropna(subset=["lat","lon",color_field]).copy()
    if safe.empty:
        # crea un df dummy para evitar figura vacía silenciosa
        safe = pd.DataFrame({
            "lat":[center[0]], "lon":[center[1]],
            "nombre":["(sin datos)"], color_field:[0.0]
        })

    # tamaños
    vals = pd.to_numeric(safe[color_field], errors="coerce").fillna(0.0).to_numpy(float)
    vals = np.clip(vals, 0, 100)
    size = np.interp(vals, [0,100], [10,40])

    fig = px.scatter_mapbox(
        safe.assign(size=size),
        lat="lat", lon="lon",
        hover_name="nombre",
        hover_data={
            "iac":":.1f" if "iac" in safe.columns else True,
            "impacto":":.1f" if "impacto" in safe.columns else True,
            "co2": True if "co2" in safe.columns else False,
            "ruido": True if "ruido" in safe.columns else False,
            "temperatura": True if "temperatura" in safe.columns else False,
            "seguridad": True if "seguridad" in safe.columns else False,
            "lat": False, "lon": False
        },
        color=color_field,
        color_continuous_scale=COLOR_SCALE,
        range_color=(0,100),
        size="size",
        size_max=45,
        zoom=zoom,
        height=650,
        custom_data=["nombre"]  # para capturar clic
    )

    fig.update_traces(marker=dict(opacity=opacity, sizemode="area"))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": center[0], "lon": center[1]},
        margin=dict(l=0,r=0,t=0,b=0),
        coloraxis_colorbar=dict(title="Impacto")
    )
    return fig


    
