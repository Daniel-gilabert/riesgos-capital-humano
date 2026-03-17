import streamlit as st
from ui.layouts.base_layout import BaseLayout
from config import get_app_name

class SettingsPage:
    """Página de configuración (placeholder para expansión futura)"""
    
    def __init__(self):
        self.layout = BaseLayout()
    
    def render(self):
        self.layout.render_header("Configuracion", f"Ajustes de {get_app_name()}")
        
        st.info("Define la estrategia de datos para Excel, Worktime o modo combinado.")
        
        # Placeholder for future settings
        st.subheader("Configuracion de la aplicacion")
        st.write("Penalizacion y conectividad Worktime/Supabase.")
        
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

        st.divider()
        st.subheader("Integracion Worktime")
        st.caption("Configura estas variables en .env o secrets.toml para activar la lectura de base Worktime.")
        st.code(
            "\n".join([
                "DATA_SOURCE=worktime  # o mixed",
                "SUPABASE_URL=...",
                "SUPABASE_KEY=...",
                "ANALISIS_TABLE=trrfp_analisis",
                "CITAS_DETALLE_TABLE=trrfp_citas_analizadas",
                "ACCESS_KEYS_TABLE=trrfp_access_keys",
                "WORKTIME_TABLE=worktime_citas",
                "WORKTIME_EMPLOYEES_TABLE=trrfp_empleados",
                "WORKTIME_DATE_COLUMN=fecha",
                "WORKTIME_EMPLOYEE_COLUMN=persona_trabajadora",
                "WORKTIME_ATTENDANCE_COLUMN=asistencia",
                "WORKTIME_CANCELED_COLUMN=anulada",
                "WORKTIME_LIMIT=5000",
                "SMTP_HOST=smtp.office365.com",
                "SMTP_PORT=587",
                "SMTP_USER=tu_correo@prode.es",
                "SMTP_PASSWORD=tu_clave_smtp",
                "SMTP_FROM=tu_correo@prode.es",
                "SMTP_USE_TLS=true",
            ]),
            language="bash",
        )
