import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="EcoLibros", page_icon="📚")

st.title("📚 Intercambio de Libros")
st.write("Publica lo que ya no usas o busca lo que necesitas.")

# --- BASE DE DATOS TEMPORAL ---
# Recordatorio: Sin Google Sheets, esto se borra al cerrar la sesión.
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Título", "Precio", "Contacto"])

# --- MENÚ ---
tab1, tab2 = st.tabs(["🔍 Buscar Libros", "📤 Ofrecer un Libro"])

with tab1:
    st.subheader("Libros disponibles")
    if st.session_state.db.empty:
        st.info("Aún no hay libros publicados. ¡Sé el primero!")
    else:
        busqueda = st.text_input("Filtrar por título").strip().lower()
        
        df_mostrar = st.session_state.db
        if busqueda:
            df_mostrar = df_mostrar[df_mostrar['Título'].str.lower().str.contains(busqueda)]
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {row['Título']}"):
                precio_txt = f"💰 Precio: {row['Precio']}" if row['Precio'] else "💰 Precio: A convenir"
                st.write(precio_txt)
                
                # Link de WhatsApp
                url_wa = f"https://wa.me/{row['Contacto']}?text=Hola, vi tu libro '{row['Título']}'"
                st.markdown(f"[📲 Contactar al vendedor]({url_wa})")
                
                st.divider()
                
                # --- SISTEMA DE CONFIRMACIÓN (OPCIÓN 2) ---
                st.warning("⚠️ ¿Ya vendiste este libro?")
                if st.button(f"SÍ, QUITAR DE LA LISTA", key=f"del_{i}"):
                    st.session_state.db = st.session_state.db.drop(i)
                    st.success("Publicación eliminada.")
                    st.rerun()

with tab2:
    st.subheader("Publica tu libro")
    with st.form("form_publicar", clear_on_submit=True):
        titulo = st.text_input("Título del libro").strip()
        precio = st.text_input("Precio (Opcional)")
        whatsapp = st.text_input("Tu WhatsApp (Ej: 5491122334455)")
        
        if st.form_submit_button("Publicar ahora"):
            if titulo and whatsapp:
                nueva_entrada = {
                    "Título": titulo,
                    "Precio": precio,
                    "Contacto": whatsapp
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nueva_entrada])], ignore_index=True)
                st.success("¡Publicado!")
                st.rerun()
            else:
                st.error("Título y WhatsApp son obligatorios.")
