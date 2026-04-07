import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="EcoLibros", page_icon="📚")
st.title("📚 Intercambio de Libros")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=5)
except Exception as e:
    st.error("Error de conexión.")
    st.stop()

tab1, tab2 = st.tabs(["🔍 Buscar Libros", "📤 Ofrecer un Libro"])

with tab1:
    if st.button("🔄 Actualizar lista"):
        st.cache_data.clear()
        st.rerun()

    if df.empty:
        st.info("No hay libros publicados aún.")
    else:
        busqueda = st.text_input("Filtrar por título").strip().lower()
        df_mostrar = df[df['Título'].astype(str).str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {str(row['Título'])}"):
                st.write(f"💰 Precio: {row['Precio'] if row['Precio'] else 'A convenir'}")
                
                num_tel = str(row['Contacto']).split('.')[0].strip()
                url_wa = f"https://wa.me/{num_tel}?text=Hola, vi tu libro '{row['Título']}'"
                
                boton_html = f"""
                    <a href="{url_wa}" target="_blank" style="
                        text-decoration: none;
                        background-color: #25D366;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 10px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 10px 0;">
                        📲 Contactar al vendedor
                    </a>
                """
                st.markdown(boton_html, unsafe_allow_html=True)
                
                st.divider()
                
                if st.button(f"SÍ, YA SE VENDIÓ", key=f"del_{i}"):
                    df_nuevo = df.drop(i)
                    conn.update(data=df_nuevo)
                    st.success("Eliminado.")
                    st.rerun()

with tab2:
    with st.form("form_pub", clear_on_submit=True):
        t = st.text_input("Título")
        p = st.text_input("Precio (Opcional)")
        w = st.text_input("WhatsApp (Ej: 54911...)")
        if st.form_submit_button("Publicar"):
            if t and w:
                w_clean = "".join(filter(str.isdigit, w))
                nueva = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w_clean}])
                df_final = pd.concat([df, nueva], ignore_index=True)
                try:
                    conn.update(data=df_final)
                    st.success("¡Publicado!")
                    st.rerun()
                except Exception as e:
                    st.error("Error al guardar.")
            else:
                st.error("Título y WhatsApp son obligatorios.")
