UrbanSense – MVP Semana 1
 1. Objetivo del proyecto

UrbenSense es una herramienta de visualización urbana basada en datos ambientales y sociales. En esta primera semana se define la arquitectura base, la estructura de carpetas y los contratos mínimos del sistema para garantizar escalabilidad.

2. Estructura del proyecto
urbansense/
 ├─ main.py                     # Interfaz principal con Streamlit
 ├─ requirements.txt           #Para descargar las librerias que se necesitan
 ├─ README.md                  # Documentación del proyecto
 ├─ data/
 │.   └─ urbansense_samplecsv  # Dataset de prueba                                           
 ├─ src/
 │   ├─ data_loader.py         # Capa de datos
 │   ├─ map_layer.py           # Capa de mapas con Plotly
 │   ├─ utils.py               # Utilidades y helpers
 │   └─ config.py              # Configuración y constantes

3. Flujo de datos
CSV (data/urbansense_sample.csv)
        |
        v
  data_loader.load_dataset()   --> valida columnas
        |
        v
         df (pandas)
        |
        v
  plot_layer.build_map_plotly(df)   --> go.Figure (Plotly)
        |
        v
        UI (Streamlit)  --> st.plotly_chart(fig)