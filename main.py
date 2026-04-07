import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="EcoLibros | Intercambio Escolar", page_icon="📚", layout="centered")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; }
    [data-testid="stExpander"] {
        border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 15px; background-color: white; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Intercambio de Libros")

def cargar_datos():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(ttl=0)

try:
    df_raw = cargar_datos()
    df = df_raw.iloc[::-1].reset_index(drop=True) if not df_raw.empty else df_raw
except:
    st.error("Error al conectar con la base de datos.")
    st.stop()

tab1, tab2 = st.tabs(["🔍 BUSCAR LIBROS", "📤 PUBLICAR MI LIBRO"])

with tab1:
    busqueda = st.text_input("¿Qué libro buscas?", placeholder="Ej: Lengua...").strip().lower()

    if df.empty:
        st.info("No hay libros publicados.")
    else:
        df_mostrar = df[df['Título'].astype(str).str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {str(row['Título']).upper()}"):
                # --- LIMPIEZA DE NOMBRE ---
                vendedor = row['Nombre'] if 'Nombre' in row and pd.notna(row['Nombre']) and str(row['Nombre']).strip() != "" else "Usuario"
                st.write(f"👤 **Vendedor:** {vendedor}")
                
                # --- LIMPIEZA DE PRECIO (Evita el $ nan) ---
                raw_precio = str
