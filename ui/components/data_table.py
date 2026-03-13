import streamlit as st
import pandas as pd

def mostrar_tabla_datos(df: pd.DataFrame, titulo: str = "Datos"):
    """Mostrar DataFrame como tabla interactiva"""
    if df.empty:
        st.info("No hay datos para mostrar")
        return
    
    st.subheader(titulo)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )