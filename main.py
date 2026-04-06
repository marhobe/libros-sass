import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="EcoLibros", page_icon="📚")

st.title("📚 Intercambio de Libros")
st.write("Publica lo que ya no usas o busca lo que necesitas.")

# --- BASE DE DATOS TEMPORAL ---
# Nota: Mientras no conectemos la base de datos permanente, 
# los datos se borrarán si la app se reinicia.
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Título", "Precio", "Contacto"])

# --- MENÚ ---
tab1, tab2 = st.tabs(["🔍 Buscar Libros", "📤 Ofrecer un Libro"])

with tab1:
    st.subheader("Libros disponibles")
    if st.session_state.db.empty:
        st.info("Aún no hay libros publicados. ¡Sé el primero en ofrecer uno!")
    else:
        busqueda = st.text_input("Filtrar por título (ej: Matemáticas)").strip().lower()
        
        # Filtrar datos
        df_mostrar = st.session_state.db
        if busqueda:
            df_mostrar = df_mostrar[df_mostrar['Título'].str.lower().contains(busqueda)]
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {row['Título']}"):
                precio_txt = f"💰 Precio: {row['Precio']}" if row['Precio'] else "💰 Precio: No especificado / A convenir"
                st.write(precio_txt)
                
                # Botón de WhatsApp (Oculta el número)
                mensaje_wa = f"Hola, vi tu libro '{row['Título']}' en la App y me interesa."
                url_wa = f"https://wa.me/{row['Contacto']}?text={mensaje_wa}"
                
                col1, col2 = st.columns([1, 1])
                col1.markdown(f"[📲 Contactar al vendedor]({url_wa})")
                
                # Botón para que el dueño lo borre
                if col2.button("Marcar como Vendido", key=f"btn_{i}"):
                    st.session_state.db = st.session_state.db.drop(i)
                    st.rerun()

with tab2:
    st.subheader("Publica tu libro")
    with st.form("form_publicar", clear_on_submit=True):
        titulo = st.text_input("Título del libro (ej: Ciencias Naturales 3)").strip()
        precio = st.text_input("Precio (Opcional - puedes dejarlo vacío)")
        whatsapp = st.text_input("Tu número de WhatsApp (Ej: 5491122334455)", help="Incluye código de país y área sin el + ni espacios.")
        
        submit = st.form_submit_button("Publicar ahora")
        
        if submit:
            if titulo and whatsapp:
                nueva_entrada = {
                    "Título": titulo,
                    "Precio": precio if precio else "A convenir",
                    "Contacto": whatsapp
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nueva_entrada])], ignore_index=True)
                st.success(f"¡Listo! Tu libro '{titulo}' ya está en la lista.")
            else:
                st.error("El título y el WhatsApp son obligatorios para que te contacten.")

st.info("💡 Tip: Para borrar un libro que ya vendiste, búscalo en la lista y presiona 'Marcar como Vendido'.")
