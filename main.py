import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="EcoLibros | Intercambio Escolar", page_icon="📚", layout="centered")

# --- ESTILO ---
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

# Función para leer datos frescos (TTL=0 para que no guarde nada en memoria)
def cargar_datos():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(ttl=0)

try:
    df_raw = cargar_datos()
    # Solo invertimos si hay datos
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
                st.metric(label="Precio", value=f"$ {row['Precio'] if row['Precio'] else 'A convenir'}")
                
                num_tel = str(row['Contacto']).split('.')[0].strip()
                url_wa = f"https://wa.me/{num_tel}?text=Hola! Me interesa tu libro '{row['Título']}'"
                
                st.markdown(f"""
                    <a href="{url_wa}" target="_blank" style="
                        text-decoration: none; background-color: #25D366; color: white;
                        padding: 12px 24px; border-radius: 25px; font-weight: bold;
                        display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 4px 10px rgba(37,211,102,0.3); margin: 10px 0;">
                        📲 CONTACTAR AL VENDEDOR
                    </a>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # BORRADO DIRECTO PARA EVITAR ERRORES DE ÍNDICE
                if st.button(f"🗑️ MARCAR COMO VENDIDO", key=f"btn_{i}"):
                    # Volvemos a leer el original para estar seguros de qué borramos
                    df_actual = cargar_datos()
                    # Buscamos la fila exacta por título y contacto (más seguro que el índice)
                    df_nuevo = df_actual[~((df_actual['Título'] == row['Título']) & (df_actual['Contacto'] == row['Contacto']))]
                    
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    conn.update(data=df_nuevo)
                    
                    st.success("¡Vendido! Actualizando lista...")
                    st.rerun()

with tab2:
    with st.form("form_pub", clear_on_submit=True):
        t = st.text_input("Título del libro")
        p = st.text_input("Precio sugerido")
        w = st.text_input("Tu WhatsApp (Ej: 54911...)")
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            if t and w:
                w_clean = "".join(filter(str.isdigit, w))
                nueva_fila = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w_clean}])
                
                df_para_guardar = pd.concat([cargar_datos(), nueva_fila], ignore_index=True)
                
                conn = st.connection("gsheets", type=GSheetsConnection)
                conn.update(data=df_para_guardar)
                
                st.balloons()
                st.rerun()
            else:
                st.error("Completa los campos obligatorios.")
