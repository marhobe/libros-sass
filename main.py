import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Configuración de página
st.set_page_config(page_title="EcoLibros | Intercambio Escolar", page_icon="📚", layout="centered")

# --- ESTILO CSS PROFESIONAL Y ADAPTABLE ---
st.markdown("""
    <style>
    /* Estilo general de botones */
    .stButton>button { 
        border-radius: 20px; 
        width: 100%;
    }
    
    /* Configuración de los Expanders (Tarjetas de libros) */
    [data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.2); 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-radius: 15px; 
        margin-bottom: 15px;
        background-color: transparent; /* Adaptable al tema */
    }

    /* Forzar que el título del expander sea visible en cualquier modo */
    [data-testid="stExpander"] summary p {
        color: inherit !important;
        font-weight: bold;
        font-size: 1.05rem;
    }

    /* Estilo para los inputs de texto */
    .stTextInput input {
        border-radius: 12px;
    }

    /* Ajuste para el separador */
    hr {
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Intercambio de Libros")

# --- FUNCIÓN DE DATOS ---
def cargar_datos():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(ttl=0)
    except Exception as e:
        st.error("No se pudo conectar con Google Sheets. Revisa la configuración.")
        return pd.DataFrame()

# Cargar DataFrame
df_raw = cargar_datos()
if not df_raw.empty:
    # Invertir para mostrar los más nuevos primero
    df = df_raw.iloc[::-1].reset_index(drop=True)
else:
    df = df_raw

# --- INTERFAZ DE TABS ---
tab1, tab2 = st.tabs(["🔍 BUSCAR LIBROS", "📤 PUBLICAR MI LIBRO"])

with tab1:
    busqueda = st.text_input("¿Qué libro buscas?", placeholder="Escribe el título aquí...").strip().lower()

    if df.empty:
        st.info("Aún no hay libros publicados. ¡Sé el primero en subir uno!")
    else:
        # Filtrado
        df_mostrar = df[df['Título'].astype(str).str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        if df_mostrar.empty:
            st.warning("No se encontraron libros con ese nombre.")
        
        for i, row in df_mostrar.iterrows():
            titulo_libro = str(row['Título']).upper()
            
            with st.expander(f"📖 {titulo_libro}"):
                # Datos del vendedor
                vendedor = row['Nombre'] if 'Nombre' in row and pd.notna(row['Nombre']) else "Usuario"
                st.write(f"👤 **Vendedor:** {vendedor}")
                
                # Lógica de precio
                raw_precio = str(row['Precio']).strip() if pd.notna(row['Precio']) else ""
                precio_display = f"$ {raw_precio}" if (raw_precio and
