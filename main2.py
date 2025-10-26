# ...existing code...
import sys
from pathlib import Path

# ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
        st.subheader("Mapa (Plotly)")
        st.caption("Si no ves puntos, revisa que lat/lon sean numéricos y el CSV tenga datos.")
        st.write("CSV cargado desde:", DEFAULT_CSV)

        df = load_dataset(str(DEFAULT_CSV))
        st.dataframe(df.head())  # diagnóstico visual

        fig = build_map_plotly(df)
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

if __name__ == "__main__":
    run_app()

