import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="EcoLibros", page_icon="📚")

st.title("📚 Intercambio de Libros")

# Intentar conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
except Exception as e:
    st.error("Error de conexión con la base de datos. Verifica los Secrets.")
    st.stop()

tab1, tab2 = st.tabs(["🔍 Buscar Libros", "📤 Ofrecer un Libro"])

with tab1:
    if df.empty:
        st.info("No hay libros publicados aún.")
    else:
        busqueda = st.text_input("Filtrar por título").strip().lower()
        df_mostrar = df[df['Título'].str.lower().str.contains(busqueda, na=False)] if busqueda else df
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {row['Título']}"):
                st.write(f"💰 Precio: {row['Precio'] if row['Precio'] else 'A convenir'}")
                url_wa = f"https://wa.me/{row['Contacto']}?text=Hola, vi tu libro '{row['Título']}'"
                st.markdown(f"[📲 Contactar al vendedor]({url_wa})")
                if st.button(f"SÍ, YA SE VENDIÓ", key=f"del_{i}"):
                    df_nuevo = df.drop(i)
                    conn.update(data=df_nuevo)
                    st.success("Eliminado. Refrescando...")
                    st.rerun()

with tab2:
    with st.form("form_pub", clear_on_submit=True):
        t = st.text_input("Título")
        p = st.text_input("Precio (Opcional)")
        w = st.text_input("WhatsApp (Ej: 54911...)")
        if st.form_submit_button("Publicar"):
            if t and w:
                nueva = pd.DataFrame([{"Título": t, "Precio": p, "Contacto": w}])
                df_f = pd.concat([df, nueva], ignore_index=True)
                conn.update(data=df_f)
                st.success("¡Publicado!")
                st.rerun()
