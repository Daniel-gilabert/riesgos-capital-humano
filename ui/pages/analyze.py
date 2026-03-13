import streamlit as st
import pandas as pd
from ui.layouts.base_layout import BaseLayout
from ui.components.data_table import mostrar_tabla_datos
from ui.components.metrics_panel import mostrar_metricas
from services.data_service import DataService
from services.analisis_service import AnalisisService

class AnalyzePage:
    """Página de análisis y resultados"""
    
    def __init__(self):
        self.layout = BaseLayout()
        self.data_service = DataService()
        self.analisis_service = AnalisisService()
    
    def render(self):
        self.layout.render_header("Análisis de Citas Médicas", "Resultados y cálculos de costos")
        
        if 'archivo_subido' not in st.session_state or st.session_state['archivo_subido'] is None:
            st.warning("Por favor suba un archivo Excel en la página de Inicio primero.")
            return
        
        archivo = st.session_state['archivo_subido']
        
        try:
            # Procesar datos
            with st.spinner("Procesando datos..."):
                citas = self.data_service.load_citas_desde_excel(archivo)
                resultados = self.analisis_service.calcular_costos(citas)
                
                # Guardar resultados en Supabase si está configurado
                if hasattr(self.data_service, 'save_analisis_result'):
                    nombre_archivo = getattr(archivo, 'name', 'archivo_desconocido')
                    analisis_id = self.data_service.save_analisis_result(resultados, nombre_archivo)
                    if analisis_id:
                        st.success(f"Análisis guardado en la base de datos con ID: {analisis_id}")
            
            # Mostrar métricas principales
            st.subheader("Resumen de Costos")
            metricas = {
                "Costo Total": f"{resultados['costo_total']:.2f} €",
                "Citas Totales": resultados['resumen']['total_citas'],
                "Citas Asistidas": resultados['resumen']['asistidas'],
                "Citas Perdidas (No Anuladas)": resultados['resumen']['perdidas_no_anuladas'],
                "Citas Anuladas": resultados['resumen']['anuladas'],
                "Citas Perdidas pero Anuladas": resultados['resumen']['perdidas_y_anuladas']
            }
            mostrar_metricas(metricas)
            
            st.divider()
            
            # Mostrar detalle de citas con costo
            if resultados['citas_con_costo']:
                st.subheader("Citas que Generan Costos")
                # Convertir a DataFrame para mostrar
                datos_para_mostrar = []
                for cita in resultados['citas_con_costo']:
                    datos_para_mostrar.append({
                        'Empleado': cita.nombre_empleado,
                        'Fecha': cita.fecha_cita.strftime('%d/%m/%Y %H:%M'),
                        'Asistió': cita.asistencia,
                        'Anulada': cita.anulada,
                        'Costo (€)': cita.obtener_monto_costo()
                    })
                df_citas = pd.DataFrame(datos_para_mostrar)
                mostrar_tabla_datos(df_citas, "Detalle de citas con costo asociado")
                
                # Desglose por empleado
                if resultados['costos_por_empleado']:
                    st.subheader("Costos por Empleado")
                    df_empleados = pd.DataFrame([
                        {'Empleado': emp, 'Costo (€)': costo}
                        for emp, costo in resultados['costos_por_empleado'].items()
                    ])
                    mostrar_tabla_datos(df_empleados, "Costos acumulados por empleado")
            else:
                st.success("¡Excelente! No hay citas que generen costos adicionales.")
                
        except Exception as e:
            st.error(f"Error procesando el archivo: {str(e)}")
            st.info("Por favor verifique que el archivo tenga el formato correcto y las columnas requeridas.")