import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="EcoLibros | Intercambio Escolar", page_icon="📚", layout="centered")

# --- DISEÑO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        border-radius: 20px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #4CAF50;
        color: white;
    }
    [data-testid="stExpander"] {
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 15px;
        background-color: white;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Intercambio de Libros")
st.markdown("##### *Dale una segunda vida a tus libros escolares*")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=5)
    # Invertir para que lo más nuevo salga arriba
    df = df.iloc[::-1] 
except Exception as e:
    st.error("Error de conexión.")
    st.stop()

tab1, tab2 = st.tabs(["🔍 BUSCAR LIBROS", "📤 PUBLICAR MI LIBRO"])

with tab1:
    col_ref, col_bus = st.columns([1, 4])
    with col_ref:
        if st.button("🔄 Refrescar"):
            st.cache_data.clear()
            st.rerun()
    with col_bus:
        busqueda = st.text_input("¿Qué libro buscas?", placeholder="Ej: Matemáticas 3...").strip().lower()

    if df.empty:
        st.info("Aún no hay libros publicados. ¡Sé el primero!")
    else:
        df_mostrar = df[df['Título'].astype(str).str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {str(row['Título']).upper()}"):
                c1, c2 = st.columns(2)
                with c1:
                    precio = row['Precio'] if row['Precio'] else 'A convenir'
                    st.metric(label="Precio", value=f"$ {precio}")
                
                num_tel = str(row['Contacto']).split('.')[0].strip()
                url_wa = f"https://wa.me/{num_tel}?text=Hola! Me interesa tu libro '{row['Título']}'"
                
                boton_html = f"""
                    <a href="{url_wa}" target="_blank" style="
                        text-decoration: none;
                        background-color: #25D366;
                        color: white;
                        padding: 12px 24px;
                        border-radius: 25px;
                        font-weight: bold;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                        box-shadow: 0 4px 10px rgba(37,211,102,0.3);
                        margin: 10px 0;">
                        📲 CONTACTAR AL VENDEDOR
                    </a>
                """
                st.markdown(boton_html, unsafe_allow_html=True)
                
                if st.button(f"🗑️ MARCAR COMO VENDIDO", key=f"btn_{i}"):
                    st.warning(f"¿Confirmas que quieres borrar '{row['Título']}'?")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ SÍ, BORRAR", key=f"conf_{i}"):
                            df_nuevo = df.drop(i)
                            conn.update(data=df_nuevo)
                            st.success("¡Borrado!")
                            st.rerun()
                    with b2:
                        if st.button("❌ CANCELAR", key=f"canc_{i}"):
                            st.rerun()

with tab2:
    st.subheader("Completa los datos del libro")
    with st.form("form_pub", clear_on_submit=True):
        t = st.text_input("Título del libro", placeholder="Ej: Lengua y Literatura 2 Santillana")
        p = st.text_input("Precio sugerido", placeholder="Ej: 5000 o 'Gratis'")
        w = st.text_input("Tu WhatsApp con código de país", placeholder="Ej: 54911...")
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            if t and w:
                w_clean = "".join(filter(str.isdigit, w))
                nueva = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w_clean}])
                df_final = pd.concat([df, nueva], ignore_index=True)
                try:
                    conn.update(data=df_final)
                    st.balloons()
                    st.success("¡Tu libro ya está disponible en la lista!")
                    st.rerun()
                except Exception as e:
                    st.error("Error al guardar.")
            else:
                st.error("Por favor completa Título y WhatsApp.")
