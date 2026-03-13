import streamlit as st

class BaseLayout:
    """Base layout for the application"""
    
    def render_header(self, titulo: str, subtitulo: str = None):
        """Render header of the page"""
        st.title(titulo)
        if subtitulo:
            st.caption(subtitulo)
        st.divider()
    
    def render_sidebar_navigation(self, paginas: list) -> str:
        """Render navigation in the sidebar"""
        with st.sidebar:
            st.title("Navegación")
            pagina = st.radio("Ir a", paginas)
        return pagina