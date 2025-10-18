# src/plot_layer.py
from .utils import color_from_iac
from .config import PLOTLY_TEMPLATE

def _go():
    try:
        import plotly.graph_objects as go
        return go
    except Exception:
        return None

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
