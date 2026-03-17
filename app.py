import streamlit as st
from ui.layouts.base_layout import BaseLayout
from ui.pages.home import HomePage
from ui.pages.analyze import AnalyzePage
from ui.pages.settings import SettingsPage
from config import get_app_name

def main():
    app_name = get_app_name()
    st.set_page_config(
        page_title=app_name,
        page_icon="assets/logo.png" if st.session_state.get("logo_path") else None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.logo_path = "assets/logo.png"
        st.session_state.user = None
        # Add any other initial state variables here
    
    # Sidebar navigation
    with st.sidebar:
        st.title(app_name)
        st.caption("Análisis y gestión de riesgos organizacionales")
        
        # Placeholder for user info
        if st.session_state.user:
            st.write(f"Usuario: {st.session_state.user}")
        else:
            st.write("Usuario: No autenticado")
        
        st.divider()
        
        # Navigation menu
        page = st.selectbox(
            "Navegación",
            ["Inicio", "Análisis", "Configuración"],
            key="navigation"
        )
        
        st.divider()
        st.caption("Versión 1.0.0")
    
    # Render selected page
    if page == "Inicio":
        HomePage().render()
    elif page == "Análisis":
        AnalyzePage().render()
    elif page == "Configuración":
        SettingsPage().render()

if __name__ == "__main__":
    main()
