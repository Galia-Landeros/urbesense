import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página (igual que antes)
st.set_page_config(layout="wide")

# 2. SECCIÓN DE CSS (Tu encabezado personalizado)
# Este encabezado estará visible SIEMPRE, en todas las secciones.
# ----------------------------------------------------------------------
header_html = """
<style>
    /* ... (Todo tu CSS va aquí dentro) ... */
    .encabezado-principal-st { font-family: Arial; }
    .barra-superior-st { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 40px; 
        border-bottom: 1px solid #ddd; 
    }
    .logo-st img { height: 50px; }
    .enlaces-utilidad-st { display: flex; gap: 15px; }
    .navegacion-principal-st { 
        background-color: #4a5568; 
        padding: 0 40px; 
    }
    .navegacion-principal-st ul { 
        display: flex; 
        list-style: none; 
        margin: 0; 
        padding: 0; 
        gap: 25px; 
    }
    .navegacion-principal-st a { 
        color: white; 
        font-weight: bold; 
        padding: 12px 0; 
        display: block; 
        text-decoration: none; 
    }
    .navegacion-principal-st a:hover { text-decoration: underline; }
</style>

<header class="encabezado-principal-st">
    <div class="barra-superior-st">
        <div class="logo-st">
            <a href="https://www.inegi.org.mx/" target="_blank">
                <img src="https://www.inegi.org.mx/img/logo_inegi_4.png" alt="Logo INEGI">
            </a>
        </div>
        <div class="enlaces-utilidad-st">
            <a href="#">[f]</a> <a href="#">[t]</a> <a href="#">English</a> <a href="#">Contacto</a>
        </div>
    </div>
    <nav class="navegacion-principal-st">
        <ul>
            <li><a href="#">Temas</a></li>
            <li><a href="#">Programas de información</a></li>
            <li><a href="#">Sistemas de Consulta</a></li>
            <li><a href="#">Desarrollo social</a></li>
        </ul>
    </nav>
</header>
"""
# Inyectar el HTML del encabezado
st.markdown(header_html, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# 3. NAVEGACIÓN DE "BOTONES" (EN LA BARRA LATERAL)
# ----------------------------------------------------------------------
st.sidebar.title("Navegación")
st.sidebar.write("Selecciona la sección que quieres ver:")

# Aquí creamos los "botones" (en formato de radio)
opcion = st.sidebar.radio(
    "Menú Principal",
    ("🏠 Inicio", "📊 Gráficos (Plotly)", "📄 Tabla de Datos")
)

# ----------------------------------------------------------------------
# 4. CONTENIDO DINÁMICO (SE REEMPLAZA SEGÚN EL BOTÓN)
# ----------------------------------------------------------------------

# Usamos if/elif para mostrar solo la sección seleccionada

if opcion == "🏠 Inicio":
    st.title("🏠 Página Principal")
    st.write("Bienvenido al dashboard interactivo. Esta es la sección de inicio.")
    st.info("Usa el menú de la izquierda para navegar a otras secciones.")
    st.image("https://www.inegi.org.mx/img/logo_inegi_4.png", width=300)

elif opcion == "📊 Gráficos (Plotly)":
    st.title("📊 Sección de Gráficos (Plotly)")
    st.write("Aquí se muestra el análisis visual con Plotly.")
    
    # Datos de ejemplo
    df_iris = px.data.iris() 
    fig = px.scatter(df_iris, x="sepal_width", y="sepal_length", color="species",
                     title="Gráfico de Plotly: Datos de Iris")
    st.plotly_chart(fig, use_container_width=True)

elif opcion == "📄 Tabla de Datos":
    st.title("📄 Sección de Tabla de Datos")
    st.write("Aquí puedes ver los datos crudos en una tabla.")
    
    # Datos de ejemplo
    df_tabla = pd.DataFrame({
        'ID de Zona': [101, 102, 103, 104],
        'Nivel de Actividad': ["Baja", "Baja", "Media", "Alta"],
        'Causa Principal': ["Falta de servicios", "Inseguridad", "Comercio", "Parque"]
    })
    st.dataframe(df_tabla, use_container_width=True)