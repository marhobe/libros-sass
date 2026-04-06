import streamlit as st
import pandas as pd

# Configuración
st.set_page_config(page_title="Libros Escolares", page_icon="📚")

st.title("📚 Intercambio de Libros")
st.write("Busca lo que necesitas o publica lo que ya no usas.")

# Simulación de base de datos en memoria
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Título", "Grado", "Precio", "Contacto"])

menu = ["Buscar", "Ofrecer"]
choice = st.sidebar.selectbox("¿Qué quieres hacer?", menu)

if choice == "Ofrecer":
    st.subheader("Publicar un libro")
    with st.form("form_ofrecer"):
        titulo = st.text_input("Título del libro").strip().capitalize()
        grado = st.selectbox("Grado/Año", ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "1° Año Sec", "2° Año Sec", "3° Año Sec"])
        precio = st.text_input("Precio (o 'Gratis')")
        contacto = st.text_input("Tu WhatsApp (Ej: 1122334455)")
        botón = st.form_submit_button("Subir publicación")
        
        if botón:
            if titulo and contacto:
                nueva_fila = {"Título": titulo, "Grado": grado, "Precio": precio, "Contacto": contacto}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.success(f"¡Publicado! {titulo} ahora está disponible.")
            else:
                st.error("Por favor completa el título y tu contacto.")

elif choice == "Buscar":
    st.subheader("Libros disponibles")
    if st.session_state.db.empty:
        st.info("Aún no hay libros publicados. ¡Sé el primero!")
    else:
        busqueda = st.text_input("Filtrar por título")
        df = st.session_state.db
        if busqueda:
            df = df[df['Título'].str.contains(busqueda, case=False)]
        
        for i, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                col1.write(f"📖 **{row['Título']}** ({row['Grado']})")
                col1.write(f"💰 Precio: {row['Precio']}")
                
                # Botón de WhatsApp
                url_wa = f"https://wa.me/{row['Contacto']}?text=Hola, me interesa el libro {row['Título']}"
                col2.markdown(f"[📲 Contactar]({url_wa})")
                
                if col2.button("Eliminar", key=i):
                    st.session_state.db = st.session_state.db.drop(i)
                    st.rerun()
                st.divider()
