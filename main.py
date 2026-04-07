import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Configuración de página
st.set_page_config(page_title="EcoLibros | Intercambio Escolar", page_icon="📚", layout="centered")

# --- ESTILO CSS ADAPTABLE (SOLUCIÓN MODO OSCURO) ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; width: 100%; }
    
    [data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.2); 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-radius: 15px; 
        margin-bottom: 15px;
        background-color: transparent;
    }

    [data-testid="stExpander"] summary p {
        color: inherit !important;
        font-weight: bold;
        font-size: 1.05rem;
    }

    .stTextInput input { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Intercambio de Libros")

# --- FUNCIÓN DE DATOS ---
def cargar_datos():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(ttl=0)
    except:
        return pd.DataFrame()

df_raw = cargar_datos()
df = df_raw.iloc[::-1].reset_index(drop=True) if not df_raw.empty else df_raw

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["🔍 BUSCAR LIBROS", "📤 PUBLICAR MI LIBRO"])

with tab1:
    busqueda = st.text_input("¿Qué libro buscas?", placeholder="Escribe el título...").strip().lower()

    if df.empty:
        st.info("No hay libros publicados.")
    else:
        df_mostrar = df[df['Título'].astype(str).str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        for i, row in df_mostrar.iterrows():
            titulo_libro = str(row['Título']).upper()
            
            with st.expander(f"📖 {titulo_libro}"):
                # Datos del vendedor
                vendedor = row['Nombre'] if 'Nombre' in row and pd.notna(row['Nombre']) else "Usuario"
                st.write(f"👤 **Vendedor:** {vendedor}")
                
                # --- LÓGICA DE PRECIO CORREGIDA ---
                raw_precio = str(row['Precio']).strip() if pd.notna(row['Precio']) else ""
                if raw_precio and raw_precio.lower() != "nan" and raw_precio != "":
                    precio_display = f"$ {raw_precio}"
                else:
                    precio_display = "A convenir"
                
                st.write(f"💰 **Precio:** {precio_display}")
                
                # Botón WhatsApp
                num_tel = "".join(filter(str.isdigit, str(row['Contacto'])))
                url_wa = f"https://wa.me/{num_tel}?text=Hola {vendedor}! Me interesa tu libro '{titulo_libro}'"
                
                st.markdown(f"""
                    <a href="{url_wa}" target="_blank" style="
                        text-decoration: none; background-color: #25D366; color: white;
                        padding: 12px; border-radius: 25px; font-weight: bold;
                        display: flex; align-items: center; justify-content: center;
                        margin: 15px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        📲 CONTACTAR POR WHATSAPP
                    </a>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Sistema de borrado
                check_key = f"delete_confirm_{i}"
                if check_key not in st.session_state:
                    st.session_state[check_key] = False

                if not st.session_state[check_key]:
                    if st.button(f"🗑️ MARCAR COMO VENDIDO", key=f"btn_{i}"):
                        st.session_state[check_key] = True
                        st.rerun()
                else:
                    st.warning("¿Confirmas que ya se vendió?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ SÍ", key=f"conf_{i}"):
                            df_actual = cargar_datos()
                            df_nuevo = df_actual[~((df_actual['Título'] == row['Título']) & (df_actual['Contacto'] == row['Contacto']))]
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            conn.update(data=df_nuevo)
                            st.session_state[check_key] = False
                            st.success("¡Eliminado!")
                            time.sleep(1)
                            st.rerun()
                    with c2:
                        if st.button("❌ NO", key=f"canc_{i}"):
                            st.session_state[check_key] = False
                            st.rerun()

with tab2:
    with st.form("form_pub", clear_on_submit=True):
        nom = st.text_input("Tu Nombre")
        t = st.text_input("Título del libro")
        p = st.text_input("Precio (Solo números o vacío)")
        w = st.text_input("Tu WhatsApp (Ej: 54911...)")
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            if t and w and nom:
                w_clean = "".join(filter(str.isdigit, w))
                nueva_fila = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w_clean, "Nombre": nom}])
                df_para_guardar = pd.concat([cargar_datos(), nueva_fila], ignore_index=True)
                conn = st.connection("gsheets", type=GSheetsConnection)
                conn.update(data=df_para_guardar)
                st.balloons()
                st.success("¡Publicado!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Completa los campos obligatorios.")
