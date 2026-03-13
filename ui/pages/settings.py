import streamlit as st
from ui.layouts.base_layout import BaseLayout

class SettingsPage:
    """Página de configuración (placeholder para expansión futura)"""
    
    def __init__(self):
        self.layout = BaseLayout()
    
    def render(self):
        self.layout.render_header("Configuración", "Ajustes y preferencias de la aplicación")
        
        st.info("Esta sección se expandirá con opciones de configuración según sus necesidades específicas.")
        
        # Placeholder for future settings
        st.subheader("Configuración de la aplicación")
        st.write("Próximamente: opciones para ajustar el valor de penalización, seleccionar columnas personalizadas, etc.")
        
        # Example: adjustable penalty amount
        penalty = st.number_input(
            "Valor de penalización por cita no asistida y no anulada (€)",
            min_value=0.0,
            value=20.0,
            step=5.0,
            help="Cambie este valor si la penalización es diferente a 20€"
        )
        st.session_state['penalty_value'] = penalty
        st.write(f"Valor de penalización actual: {penalty} €")