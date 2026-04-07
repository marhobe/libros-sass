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
                raw_precio = str(row['Precio']).strip() if pd.notna(row['Precio']) else ""
                if raw_precio != "" and raw_precio.lower() != "nan":
                    precio_display = f"$ {raw_precio}"
                else:
                    precio_display = "A convenir"
                
                st.metric(label="Precio", value=precio_display)
                
                # --- WHATSAPP ---
                num_tel = str(row['Contacto']).split('.')[0].strip()
                url_wa = f"https://wa.me/{num_tel}?text=Hola {vendedor}! Me interesa tu libro '{row['Título']}'"
                
                st.markdown(f"""
                    <a href="{url_wa}" target="_blank" style="
                        text-decoration: none; 
                        background-color: #4A90E2; 
                        color: white;
                        padding: 12px 24px; 
                        border-radius: 25px; 
                        font-weight: bold;
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        box-shadow: 0 4px 10px rgba(74,144,226,0.3); 
                        margin: 10px 0;">
                        📲 CONTACTAR AL VENDEDOR
                    </a>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                check_key = f"delete_confirm_{i}"
                if check_key not in st.session_state:
                    st.session_state[check_key] = False

                if not st.session_state[check_key]:
                    if st.button(f"🗑️ MARCAR COMO VENDIDO", key=f"btn_{i}"):
                        st.session_state[check_key] = True
                        st.rerun()
                else:
                    st.warning(f"¿Confirmas que quieres borrar '{row['Título']}'?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ SÍ, BORRAR", key=f"conf_{i}"):
                            df_actual = cargar_datos()
                            df_nuevo = df_actual[~((df_actual['Título'] == row['Título']) & (df_actual['Contacto'] == row['Contacto']))]
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            conn.update(data=df_nuevo)
                            st.session_state[check_key] = False
                            st.success("¡Vendido!")
                            st.rerun()
                    with col2:
                        if st.button("❌ CANCELAR", key=f"canc_{i}"):
                            st.session_state[check_key] = False
                            st.rerun()

with tab2:
    with st.form("form_pub", clear_on_submit=True):
        nom = st.text_input("Tu Nombre")
        t = st.text_input("Título del libro")
        p = st.text_input("Precio - Opcional (sin puntos ni comas)")
        w = st.text_input("Tu WhatsApp (Ej: 54911...)")
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            if t and w and nom:
                w_clean = "".join(filter(str.isdigit, w))
                nueva_fila = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w_clean, "Nombre": nom}])
                df_para_guardar = pd.concat([cargar_datos(), nueva_fila], ignore_index=True)
                conn = st.connection("gsheets", type=GSheetsConnection)
                conn.update(data=df_para_guardar)
                st.balloons()
                st.rerun()
            else:
                st.error("Nombre, Título y WhatsApp son obligatorios.")
