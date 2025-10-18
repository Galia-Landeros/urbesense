import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

"""UI base (Streamlit) para Semana 1 - Lunes."""
try:
    import streamlit as st
except Exception:
    st = None

from src.data_loader import load_dataset
from src.plot_layer import build_map_plotly
from src.config import DEFAULT_CSV

def run_app():
    if st is None:
        print("Streamlit no está instalado aún. Esto se completa el martes.")
        return

    st.set_page_config(page_title="UrbeSense", layout="wide")
    st.sidebar.title("UrbeSense — Panel")

    st.title("UrbeSense — Dashboard urbano (base)")
    tab_mapa, tab_about = st.tabs(["Mapa", "Acerca de"])

    with tab_mapa:
        st.subheader("Mapa (Plotly) — placeholder Lunes")
        df = load_dataset(str(DEFAULT_CSV))
        fig = build_map_plotly(df)
        # Si aún no hay Plotly instalado, el stub devuelve un dict
        if isinstance(fig, dict) and fig.get("placeholder"):
            st.info(fig["message"])
            st.json({"puntos": fig["n_points"]})
        else:
            st.plotly_chart(fig, use_container_width=True)

    with tab_about:
        st.markdown("""
        **Versión base (Lunes):** arquitectura, módulos y contratos listos.
        Mañana se instalan librerías y se activa el mapa Plotly real.
        """)

if __name__ == "__main2__":
    run_app()
