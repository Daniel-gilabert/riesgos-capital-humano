import streamlit as st

def cargar_archivo_excel() -> object:
    """Componente para subir archivo Excel"""
    archivo = st.file_uploader(
        "Seleccione el archivo Excel con los datos de citas médicas",
        type=['xlsx', 'xls'],
        help="El archivo debe contener las columnas: fecha, persona trabajadora, asistencia, anulada"
    )
    return archivo