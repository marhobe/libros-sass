import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración visual
st.set_page_config(page_title="EcoLibros", page_icon="📚")

st.title("📚 Intercambio de Libros")
st.write("Base de datos compartida para todos los padres.")

# --- CONEXIÓN AUTOMÁTICA CON GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos actuales (limpia la caché cada 2 minutos para ver cambios de otros)
df = conn.read()

tab1, tab2 = st.tabs(["🔍 Buscar Libros", "📤 Ofrecer un Libro"])

with tab1:
    st.subheader("Libros disponibles")
    if df.empty:
        st.info("Aún no hay libros publicados.")
    else:
        busqueda = st.text_input("Filtrar por título").strip().lower()
        df_mostrar = df
        if busqueda:
            df_mostrar = df[df['Título'].str.lower().str.contains(busqueda, na=False)]
        
        for i, row in df_mostrar.iterrows():
            with st.expander(f"📖 {row['Título']}"):
                precio_txt = f"💰 Precio: {row['Precio']}" if row['Precio'] else "💰 Precio: A convenir"
                st.write(precio_txt)
                
                url_wa = f"https://wa.me/{row['Contacto']}?text=Hola, vi tu libro '{row['Título']}'"
                st.markdown(f"[📲 Contactar al vendedor]({url_wa})")
                
                st.divider()
                st.warning("⚠️ ¿Ya vendiste este libro?")
                if st.button(f"SÍ, QUITAR DE LA LISTA", key=f"del_{i}"):
                    # Eliminar la fila, actualizar el Excel y recargar
                    df_nuevo = df.drop(i)
                    conn.update(data=df_nuevo)
                    st.success("Eliminado correctamente.")
                    st.rerun()

with tab2:
    st.subheader("Publica tu libro")
    with st.form("form_publicar", clear_on_submit=True):
        titulo = st.text_input("Título del libro").strip()
        precio = st.text_input("Precio (Opcional)")
        whatsapp = st.text_input("Tu WhatsApp (Ej: 5491122334455)")
        
        if st.form_submit_button("Publicar ahora"):
            if titulo and whatsapp:
                nueva_entrada = pd.DataFrame([{"Título": titulo, "Precio": precio, "Contacto": whatsapp}])
                df_final = pd.concat([df, nueva_entrada], ignore_index=True)
                conn.update(data=df_final)
                st.success("¡Publicado para todos los padres!")
                st.rerun()
            else:
                st.error("Título y WhatsApp son obligatorios.")
