# src/plot_layer.py
from .utils import color_from_iac
from .config import PLOTLY_TEMPLATE

def _go():
    try:
        import plotly.graph_objects as go
        return go
    except Exception:
        return None


# ============================================================
# 🌎 MAPA BASE: build_map_plotly (tu versión original)
# ============================================================
def build_map_plotly(df):
    go = _go()
    if go is None:
        return {"placeholder": True, "message": "Plotly no instalado", "n_points": int(len(df))}

    # asegurar tipos numéricos
    df = df.copy()
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    colors = [color_from_iac(iac) for iac in df["iac"]]

    # centro y zoom automáticos
    center_lat = df["lat"].mean() if len(df) else 0
    center_lon = df["lon"].mean() if len(df) else 0

    fig = go.Figure(
        go.Scattermapbox(
            lat=df["lat"],
            lon=df["lon"],
            mode="markers",
            marker=dict(size=12, color=colors, opacity=0.9),
            text=(
                "Zona: " + df["nombre"].astype(str)
                + "<br>IAC: " + df["iac"].astype(str)
                + "<br>Ruido: " + df["ruido"].astype(str) + " dB"
                + "<br>CO₂: " + df["co2"].astype(str) + " ppm"
                + "<br>T°: " + df["temperatura"].astype(str) + " °C"
            ),
            hoverinfo="text",
        )
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE or "plotly_white",
        mapbox=dict(
            style="open-street-map",         # no requiere token
            center=dict(lat=center_lat, lon=center_lon),
            zoom=12 if len(df) else 2,
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
        # fondos transparentes para que se vea bien en tema oscuro
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ============================================================
# 🟢 NUEVO: MAPA DE BURBUJAS (para simulador / IAC como tamaño+color)
# ============================================================
def bubble_map_iac_mapbox(
    df,
    zoom=12.0,
    center=None,
    range_size=(10, 36),
    show_legend=False,
):
    """
    Mapa de burbujas con Plotly Mapbox:
    - Color por IAC usando utils.color_from_iac (tus colores predeterminados).
    - Tamaño proporcional a IAC (0–100) escalado a range_size.
    - Center/zoom configurables; si no se da center, usa promedio del df.
    - Sin animación temporal (reactivo a cambios del df).
    Requiere columnas: ['nombre','lat','lon','iac'] y opcional ['ruido','co2','temperatura','fecha','hora'].
    """
    go = _go()
    if go is None:
        return {"placeholder": True, "message": "Plotly no instalado", "n_points": int(len(df))}

    import numpy as np
    import pandas as pd

    d = df.copy()

    # Asegurar numéricos
    for c in ("lat", "lon", "iac"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")

    d = d.dropna(subset=["lat", "lon", "iac"])
    if d.empty:
        fig = go.Figure()
        fig.update_layout(template=PLOTLY_TEMPLATE or "plotly_white")
        return fig

    # — Escalado defensivo: si IAC viene en 0–1, escalar a 0–100 —
    try:
        iac_max = float(pd.to_numeric(d["iac"], errors="coerce").max())
    except Exception:
        iac_max = 100.0
    if iac_max <= 1.5:
        d["iac"] = pd.to_numeric(d["iac"], errors="coerce") * 100.0

    # Colores desde tu helper (asume IAC 0–100)
    colors = [color_from_iac(float(v)) for v in d["iac"].values]

    # Tamaño de burbuja (área) mapeado 0–100 -> range_size
    iac_clip = np.clip(d["iac"].astype(float).values, 0.0, 100.0)
    s_min, s_max = range_size
    sizes = s_min + (s_max - s_min) * (iac_clip / 100.0)

    # Centro automático si no se pasa
    if center is None:
        center = {"lat": float(d["lat"].mean()), "lon": float(d["lon"].mean())}

    # Info de hover (opcional/robusto)
    nombre = d["nombre"].astype(str) if "nombre" in d else pd.Series(["Zona"] * len(d))
    ruido = d["ruido"] if "ruido" in d else pd.Series([np.nan] * len(d))
    co2 = d["co2"] if "co2" in d else pd.Series([np.nan] * len(d))
    temp = d["temperatura"] if "temperatura" in d else pd.Series([np.nan] * len(d))
    if {"fecha", "hora"}.issubset(d.columns):
        tiempo = (d["fecha"].astype(str) + " " + d["hora"].astype(str)).values
    else:
        tiempo = [""] * len(d)

    fig = go.Figure(
        go.Scattermapbox(
            lat=d["lat"],
            lon=d["lon"],
            mode="markers",
            marker=dict(
                sizemode="area",
                size=sizes,
                sizemin=s_min,
                color=colors,
                opacity=0.9,
            ),
            text=nombre,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "IAC: %{customdata[0]:.1f}<br>"
                "Ruido: %{customdata[1]:.0f} dB<br>"
                "CO₂: %{customdata[2]:.0f} ppm<br>"
                "Temp: %{customdata[3]:.1f} °C<br>"
                "Tiempo: %{customdata[4]}<extra></extra>"
            ),
            customdata=np.column_stack([iac_clip, ruido.values, co2.values, temp.values, tiempo]),
            hoverinfo="text",
            name="IAC (burbujas)",
            showlegend=show_legend,
        )
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE or "plotly_white",
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center["lat"], lon=center["lon"]),
            zoom=zoom if len(d) else 2,
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


