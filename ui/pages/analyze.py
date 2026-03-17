import streamlit as st
import pandas as pd
from ui.layouts.base_layout import BaseLayout
from ui.components.data_table import mostrar_tabla_datos
from ui.components.metrics_panel import mostrar_metricas
from services.data_service import DataService
from services.analisis_service import AnalisisService
from config import get_app_name, get_data_source

class AnalyzePage:
    """Página de análisis y resultados"""
    
    def __init__(self):
        self.layout = BaseLayout()
        self.data_service = DataService()
        self.analisis_service = AnalisisService()
    
    def render(self):
        self.layout.render_header("Analisis Integrado", f"{get_app_name()} - resultados y costos")

        source_mode = st.session_state.get('source_mode', get_data_source().lower())
        archivo = st.session_state.get('archivo_subido')
        
        try:
            # Procesar datos
            with st.spinner("Procesando datos..."):
                source_label = ""
                if source_mode == "worktime":
                    citas = self.data_service.load_citas_desde_worktime()
                    source_label = "Worktime"
                elif source_mode == "combinado":
                    citas_worktime = self.data_service.load_citas_desde_worktime()
                    if archivo is not None:
                        citas_excel = self.data_service.load_citas_desde_excel(archivo)
                    else:
                        citas_excel = []
                    citas, duplicados = self.data_service.combinar_citas(citas_worktime, citas_excel)
                    source_label = f"Combinado (dup. descartados: {duplicados})"
                else:
                    if archivo is None:
                        st.warning("Sube un archivo Excel en Inicio o cambia la fuente de datos.")
                        return
                    citas = self.data_service.load_citas_desde_excel(archivo)
                    source_label = "Excel"

                penalizacion = float(st.session_state.get("penalty_value", 20.0))
                resultados = self.analisis_service.calcular_costos(citas, penalizacion=penalizacion)
                st.caption(f"Fuente usada: {source_label}")
                
                # Guardar resultados en Supabase si está configurado
                if hasattr(self.data_service, 'save_analisis_result'):
                    nombre_archivo = getattr(archivo, 'name', source_label)
                    analisis_id = self.data_service.save_analisis_result(resultados, nombre_archivo)
                    if analisis_id:
                        st.success(f"Análisis guardado en la base de datos con ID: {analisis_id}")

            reporte_carga = getattr(self.data_service, "last_load_report", None)
            if reporte_carga:
                total = reporte_carga.get("total_rows", 0)
                cargadas = reporte_carga.get("loaded_rows", 0)
                omitidas = reporte_carga.get("skipped_rows", 0)
                st.caption(f"Filas procesadas: {cargadas}/{total} (omitidas: {omitidas})")
                if omitidas > 0:
                    razones = reporte_carga.get("skip_reasons", {})
                    st.warning(f"Se omitieron filas por calidad de datos: {razones}")
            
            # Mostrar métricas principales
            st.subheader("Resumen de Costos")
            metricas = {
                "Costo Total": f"{resultados['costo_total']:.2f} €",
                "Penalización aplicada": f"{resultados['penalizacion_aplicada']:.2f} €",
                "Citas Totales": resultados['resumen']['total_citas'],
                "Citas Asistidas": resultados['resumen']['asistidas'],
                "Citas Perdidas (No Anuladas)": resultados['resumen']['perdidas_no_anuladas'],
                "Citas Anuladas": resultados['resumen']['anuladas'],
                "Citas Perdidas pero Anuladas": resultados['resumen']['perdidas_y_anuladas']
            }
            mostrar_metricas(metricas)

            st.caption(
                f"Asistencia: {resultados['resumen']['porcentaje_asistencia']:.1f}% | "
                f"Perdidas con costo: {resultados['resumen']['porcentaje_perdidas']:.1f}%"
            )
            
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
                    ]).sort_values(by='Costo (€)', ascending=False)
                    mostrar_tabla_datos(df_empleados, "Costos acumulados por empleado")

                    csv_bytes = df_empleados.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Descargar costos por empleado (CSV)",
                        data=csv_bytes,
                        file_name="costos_por_empleado.csv",
                        mime="text/csv",
                    )

                    empleados_worktime = self.data_service.get_empleados_worktime_index()
                    if empleados_worktime:
                        enriquecido_rows = []
                        for _, row in df_empleados.iterrows():
                            empleado = str(row["Empleado"]).strip()
                            info = empleados_worktime.get(empleado.lower(), {})
                            enriquecido_rows.append(
                                {
                                    "Empleado": empleado,
                                    "Departamento": info.get("departamento", "Sin departamento"),
                                    "Email": info.get("email", ""),
                                    "Costo (€)": float(row["Costo (€)"]),
                                }
                            )

                        df_enriquecido = pd.DataFrame(enriquecido_rows)
                        st.subheader("Costos por Empleado (catalogo Worktime)")
                        mostrar_tabla_datos(df_enriquecido, "Cruce con base de empleados Worktime")

                        if "Departamento" in df_enriquecido.columns:
                            st.subheader("Costos por Departamento")
                            df_departamento = (
                                df_enriquecido.groupby("Departamento", as_index=False)["Costo (€)"]
                                .sum()
                                .sort_values(by="Costo (€)", ascending=False)
                            )
                            mostrar_tabla_datos(df_departamento, "Totales por departamento")
            else:
                st.success("¡Excelente! No hay citas que generen costos adicionales.")
                
        except Exception as e:
            st.error(f"Error procesando el archivo: {str(e)}")
            st.info("Por favor verifique que el archivo tenga el formato correcto y las columnas requeridas.")
