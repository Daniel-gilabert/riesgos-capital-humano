import streamlit as st
from ui.layouts.base_layout import BaseLayout
from ui.components.file_uploader import cargar_archivo_excel

class HomePage:
    """Página de inicio con carga de archivos"""
    
    def __init__(self):
        self.layout = BaseLayout()
    
    def render(self):
        self.layout.render_header("Analizador de Citas Médicas", "Cálculo de costos por citas no asistidas y no anuladas")
        
        archivo = cargar_archivo_excel()
        
        if archivo is not None:
            st.success(f"Archivo cargado: {archivo.name}")
            # Guardar en session state para usar en otras páginas
            st.session_state['archivo_subido'] = archivo
            st.info("Navega a la página 'Análisis' para procesar los datos.")
        else:
            st.info("Por favor suba un archivo Excel para comenzar el análisis.")