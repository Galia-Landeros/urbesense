"""Visualizaciones con Plotly (mapa y gráficos)."""
from .utils import color_from_iac
from .config import PLOTLY_TEMPLATE, MAPBOX_TOKEN

def _try_import_plotly():
    try:
        import plotly.graph_objects as go
        return go
    except Exception:
        return None

def build_map_plotly(df):
    """Devuelve un go.Figure con puntos georreferenciados coloreados por IAC.
    Modo seguro: si Plotly no está instalado todavía, devuelve un dict placeholder.
    """
    go = _try_import_plotly()
    if go is None:
        # placeholder para que el repo no truene el lunes
        return {
            "placeholder": True,
            "message": "Plotly no está instalado aún. Se habilitará el martes.",
            "n_points": int(len(df))
        }

    # Definir colores por fila
    colors = [color_from_iac(iac) for iac in df["iac"]]

    # Si tienes MAPBOX_TOKEN, podemos usar scattermapbox (martes).
    # Hoy usamos scattergeo (no requiere token) para mantenerlo simple.
    fig = go.Figure(
        data=[
            go.Scattergeo(
                lon=df["lon"],
                lat=df["lat"],
                text=(
                    "Zona: " + df["nombre"].astype(str)
                    + "<br>IAC: " + df["iac"].astype(str)
                    + "<br>Ruido: " + df["ruido"].astype(str) + " dB"
                    + "<br>CO₂: " + df["co2"].astype(str) + " ppm"
                    + "<br>T°: " + df["temperatura"].astype(str) + " °C"
                ),
                mode="markers",
                marker=dict(size=10, color=colors, opacity=0.9),
                hoverinfo="text",
            )
        ]
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Mapa (Plotly) — IAC por zona",
        geo=dict(
            projection_type="natural earth",  # martes lo cambiamos a 'equirectangular' o mapbox
            showcountries=False, showland=True, landcolor="rgb(240,240,240)",
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
