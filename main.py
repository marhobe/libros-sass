# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; }
    
    /* Configuración del Expander adaptable */
    [data-testid="stExpander"] {
        border: none; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 15px; 
        margin-bottom: 15px;
        /* Quitamos el background-color fijo para que Streamlit use el del tema */
    }

    /* Si quieres mantener un fondo distinto, usa variables de Streamlit: */
    div[data-testid="stExpander"] div[role="button"] p {
        font-weight: bold;
    }
    
    /* Esto asegura que el texto dentro del expander siempre contraste */
    [data-testid="stExpander"] .stMarkdown {
        color: inherit; 
    }
    </style>
    """, unsafe_allow_html=True)
