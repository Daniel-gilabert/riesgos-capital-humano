import streamlit as st
from ui.layouts.base_layout import BaseLayout
from ui.components.file_uploader import cargar_archivo_excel
from config import get_app_name, get_data_source

class HomePage:
    """Página de inicio con carga de archivos"""
    
    def __init__(self):
        self.layout = BaseLayout()
    
    def render(self):
        self.layout.render_header(
            get_app_name(),
            "Análisis de riesgos de citas médicas con integración Worktime + Excel",
        )

        source_default = (get_data_source() or "worktime").lower()
        default_index_map = {
            "excel": 0,
            "worktime": 1,
            "mixed": 2,
            "combinado": 2,
        }

        modo_fuente = st.radio(
            "Fuente de datos",
            options=["Excel", "Worktime", "Combinado"],
            index=default_index_map.get(source_default, 1),
            horizontal=True,
            help="Combinado usa datos de Worktime y suma las filas de Excel que subas aquí.",
        )
        st.session_state['source_mode'] = modo_fuente.lower()

        if modo_fuente in ("Excel", "Combinado"):
            archivo = cargar_archivo_excel()
            if archivo is not None:
                nombre_archivo = getattr(archivo, "name", "archivo_excel")
                st.success(f"Archivo cargado: {nombre_archivo}")
                st.session_state['archivo_subido'] = archivo
            elif modo_fuente == "Excel":
                st.info("Por favor suba un archivo Excel para comenzar el análisis.")
            else:
                st.info("Opcional: sube un Excel para complementar los datos de Worktime.")
        else:
            st.session_state['archivo_subido'] = None
            st.info("Se usará la base de Worktime. Configura credenciales en la sección Configuración.")

        st.info("Navega a la página 'Análisis' para procesar los datos.")
