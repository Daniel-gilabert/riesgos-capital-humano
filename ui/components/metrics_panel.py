import streamlit as st

def mostrar_metricas(metricas: dict):
    """Mostrar métricas en columnas"""
    if not metricas:
        return
    
    cols = st.columns(len(metricas))
    for i, (label, valor) in enumerate(metricas.items()):
        with cols[i]:
            st.metric(label, valor)