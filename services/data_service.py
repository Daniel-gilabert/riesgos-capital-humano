"""
Data Service for loading and preparing data for analysis
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DataService:
    """Service for loading and preparing data"""

    def __init__(self):
        self.last_load_report: Dict[str, Any] = {
            "total_rows": 0,
            "loaded_rows": 0,
            "skipped_rows": 0,
            "skip_reasons": {},
        }

    @staticmethod
    def _normalizar_texto(valor: Any) -> str:
        if valor is None:
            return ""
        if isinstance(valor, float) and np.isnan(valor):
            return ""
        return str(valor).strip()

    @staticmethod
    def _es_vacio(valor: Any) -> bool:
        return valor is None or (isinstance(valor, float) and np.isnan(valor)) or str(valor).strip() == ""

    def _agregar_error_fila(self, motivo: str):
        current = self.last_load_report["skip_reasons"].get(motivo, 0)
        self.last_load_report["skip_reasons"][motivo] = current + 1

    def _build_cita_desde_fila(
        self,
        nombre: Any,
        fecha_raw: Any,
        asistencia: Any,
        anulada: Any,
    ):
        from models.base_model import CitaMedica

        nombre_texto = self._normalizar_texto(nombre)
        asistencia_texto = self._normalizar_texto(asistencia)
        anulada_texto = self._normalizar_texto(anulada)

        if self._es_vacio(nombre_texto):
            self._agregar_error_fila("nombre_empleado_vacio")
            return None
        if self._es_vacio(fecha_raw):
            self._agregar_error_fila("fecha_vacia")
            return None
        if self._es_vacio(asistencia_texto):
            self._agregar_error_fila("asistencia_vacia")
            return None
        if self._es_vacio(anulada_texto):
            self._agregar_error_fila("anulada_vacia")
            return None

        fecha = pd.to_datetime(fecha_raw, errors="coerce")
        if pd.isna(fecha):
            self._agregar_error_fila("fecha_invalida")
            return None

        return CitaMedica(
            nombre_empleado=nombre_texto,
            fecha_cita=fecha.to_pydatetime() if hasattr(fecha, "to_pydatetime") else fecha,
            asistencia=asistencia_texto,
            anulada=anulada_texto,
        )
    
    def load_citas_desde_excel(self, archivo_subido) -> list:
        """
        Cargar citas médicas desde un archivo Excel subido
        
        Args:
            archivo_subido: Objeto de archivo subido mediante Streamlit
            
        Returns:
            Lista de objetos CitaMedica
        """
        # Import models locally to avoid circular imports
        from models.base_model import CitaMedica
        
        if hasattr(archivo_subido, "seek"):
            archivo_subido.seek(0)

        # Leer el archivo Excel
        df = pd.read_excel(archivo_subido)

        self.last_load_report = {
            "total_rows": int(len(df)),
            "loaded_rows": 0,
            "skipped_rows": 0,
            "skip_reasons": {},
        }
        
        # Validar columnas requeridas (insensible a mayúsculas/minúsculas)
        columnas_requeridas = ['fecha', 'persona trabajadora', 'asistencia', 'anulada']
        # Crear mapeo de nombres normalizados a nombres reales
        columnas_disponibles = {col.strip().lower(): col for col in df.columns}
        columnas_faltantes = []
        mapeo_columnas = {}
        
        for col_req in columnas_requeridas:
            col_req_normalizado = col_req.strip().lower()
            if col_req_normalizado in columnas_disponibles:
                mapeo_columnas[col_req] = columnas_disponibles[col_req_normalizado]
            else:
                columnas_faltantes.append(col_req)
                
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas: {columnas_faltantes}. Columnas disponibles: {list(df.columns)}")
        
        # Convertir a objetos de cita
        citas = []
        for idx, fila in df.iterrows():
            try:
                cita = self._build_cita_desde_fila(
                    fila[mapeo_columnas['persona trabajadora']],
                    fila[mapeo_columnas['fecha']],
                    fila[mapeo_columnas['asistencia']],
                    fila[mapeo_columnas['anulada']],
                )
                if cita is None:
                    continue

                citas.append(cita)
                self.last_load_report["loaded_rows"] += 1
            except Exception as e:
                self._agregar_error_fila("error_desconocido")
                logger.warning(f"Error procesando fila {idx}: {e}")
                continue

        self.last_load_report["skipped_rows"] = (
            self.last_load_report["total_rows"] - self.last_load_report["loaded_rows"]
        )

        if not citas:
            raise ValueError(
                "No se pudo procesar ninguna fila valida del archivo. "
                "Revise formato de fechas y campos requeridos."
            )
        
        return citas

    def load_citas_desde_worktime(self) -> list:
        """Cargar citas médicas desde base Worktime (vía Supabase)."""
        try:
            from config import (
                get_supabase_url,
                get_supabase_key,
                get_worktime_table,
                get_worktime_date_column,
                get_worktime_employee_column,
                get_worktime_attendance_column,
                get_worktime_canceled_column,
                get_worktime_limit,
            )
            import supabase
        except ImportError as exc:
            raise RuntimeError("Dependencias o configuración de Worktime no disponibles.") from exc

        supabase_url = get_supabase_url()
        supabase_key = get_supabase_key()
        if not supabase_url or not supabase_key:
            raise RuntimeError("Faltan SUPABASE_URL y/o SUPABASE_KEY para leer Worktime.")

        table = get_worktime_table()
        date_col = get_worktime_date_column()
        emp_col = get_worktime_employee_column()
        att_col = get_worktime_attendance_column()
        can_col = get_worktime_canceled_column()
        limit = get_worktime_limit()

        client = supabase.create_client(supabase_url, supabase_key)
        query = client.table(table).select(f"{date_col},{emp_col},{att_col},{can_col}").limit(limit)
        result = query.execute()
        rows = result.data or []

        self.last_load_report = {
            "total_rows": int(len(rows)),
            "loaded_rows": 0,
            "skipped_rows": 0,
            "skip_reasons": {},
        }

        citas = []
        for row in rows:
            cita = self._build_cita_desde_fila(
                row.get(emp_col),
                row.get(date_col),
                row.get(att_col),
                row.get(can_col),
            )
            if cita is None:
                continue
            citas.append(cita)
            self.last_load_report["loaded_rows"] += 1

        self.last_load_report["skipped_rows"] = (
            self.last_load_report["total_rows"] - self.last_load_report["loaded_rows"]
        )

        if not citas:
            raise ValueError(
                "No se recuperaron citas validas desde Worktime. "
                "Revise tabla, columnas y contenido."
            )

        return citas

    @staticmethod
    def combinar_citas(citas_a: list, citas_b: list) -> Tuple[list, int]:
        """Combina dos listas de citas y elimina duplicados por empleado+fecha."""
        combinadas = []
        vistos = set()
        duplicados = 0

        for cita in (citas_a or []) + (citas_b or []):
            fecha = cita.fecha_cita.isoformat() if cita.fecha_cita else ""
            key = (cita.nombre_empleado.strip().lower(), fecha)
            if key in vistos:
                duplicados += 1
                continue
            vistos.add(key)
            combinadas.append(cita)

        return combinadas, duplicados

    def get_empleados_worktime_index(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve indice por nombre normalizado con datos del catalogo empleados de Worktime."""
        try:
            from config import get_supabase_url, get_supabase_key, get_worktime_employees_table
            import supabase
        except ImportError:
            return {}

        supabase_url = get_supabase_url()
        supabase_key = get_supabase_key()
        if not supabase_url or not supabase_key:
            return {}

        client = supabase.create_client(supabase_url, supabase_key)
        table = get_worktime_employees_table()

        try:
            response = (
                client.table(table)
                .select("id,apellidos_y_nombre,departamento,email,responsable_id,activo")
                .eq("activo", True)
                .execute()
            )
        except Exception as exc:
            logger.warning("No se pudo leer tabla %s: %s. Probando fallback 'empleados'.", table, exc)
            try:
                response = (
                    client.table("empleados")
                    .select("id,apellidos_y_nombre,departamento,email,responsable_id,activo")
                    .eq("activo", True)
                    .execute()
                )
            except Exception as fallback_exc:
                logger.warning("No se pudo leer catalogo de empleados Worktime: %s", fallback_exc)
                return {}

        empleados = response.data or []
        index: Dict[str, Dict[str, Any]] = {}
        for item in empleados:
            nombre = self._normalizar_texto(item.get("apellidos_y_nombre"))
            if not nombre:
                continue
            index[nombre.lower()] = item
        return index
    
    def save_analisis_result(self, resultados: Dict[str, Any], nombre_archivo: str) -> Optional[str]:
        """
        Guardar resultados del análisis en Supabase (si está configurado)
        
        Args:
            resultados: Diccionario con los resultados del análisis
            nombre_archivo: Nombre del archivo original analizado
            
        Returns:
            ID del registro guardado o None si no se pudo guardar
        """
        try:
            # Importar aquí para evitar dependencias circulares si Supabase no está instalado
            from config import (
                get_data_source,
                get_supabase_url,
                get_supabase_key,
                get_analisis_table,
            )
            import supabase
            
            data_source = get_data_source()
            if data_source != "supabase":
                logger.info("Supabase no configurado como fuente de datos, omitiendo guardado")
                return None
                
            supabase_url = get_supabase_url()
            supabase_key = get_supabase_key()
            
            if not supabase_url or not supabase_key:
                logger.warning("Credenciales de Supabase no configuradas")
                return None
            
            # Crear cliente Supabase
            supabase_client = supabase.create_client(supabase_url, supabase_key)
            
            # Preparar datos para guardar
            analisis_data = {
                "fecha_analisis": datetime.now().isoformat(),
                "nombre_archivo": nombre_archivo,
                "total_citas": resultados['resumen']['total_citas'],
                "costo_total": resultados['costo_total'],
                "datos_resumen": json.dumps(resultados['resumen']),
                "creado_en": datetime.now().isoformat()
            }
            
            analisis_table = get_analisis_table()

            # Insertar en tabla analisis del proyecto
            result = supabase_client.table(analisis_table).insert(analisis_data).execute()
            
            if result.data and len(result.data) > 0:
                analisis_id = result.data[0]['id']
                logger.info(f"Análisis guardado en Supabase con ID: {analisis_id}")
                
                # También guardar detalle de citas si es relevante
                # (esto sería opcional dependiendo de las necesidades)
                # self._save_citas_detalle(supabase_client, analisis_id, resultados)
                
                return analisis_id
            else:
                logger.error("Error al guardar análisis en Supabase: no se devolvió datos")
                return None
                
        except ImportError:
            logger.warning("Supabase no instalado. Instalar con: pip install supabase")
            return None
        except Exception as e:
            logger.error(f"Error al guardar análisis en Supabase: {str(e)}")
            return None
    
    def _save_citas_detalle(self, supabase_client, analisis_id: str, resultados: Dict[str, Any]):
        """Guardar detalle de citas analizadas (método interno opcional)"""
        try:
            from config import get_citas_detalle_table

            citas_data = []
            for cita in resultados.get('citas_con_costo', []):
                citas_data.append({
                    "analisis_id": analisis_id,
                    "nombre_empleado": cita.nombre_empleado,
                    "fecha_cita": cita.fecha_cita.isoformat() if cita.fecha_cita else None,
                    "asistio": cita.asistio(),
                    "anulada": cita.fue_anulada(),
                    "genera_costo": cita.genera_costo(),
                    "monto_costo": cita.obtener_monto_costo()
                })
            
            if citas_data:
                supabase_client.table(get_citas_detalle_table()).insert(citas_data).execute()
                logger.info(f"Guardados {len(citas_data)} registros de detalle de citas")
        except Exception as e:
            logger.error(f"Error al guardar detalle de citas: {str(e)}")
    
    def get_historial_analisis(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener historial de análisis desde Supabase
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de análisis realizados
        """
        try:
            from config import (
                get_data_source,
                get_supabase_url,
                get_supabase_key,
                get_analisis_table,
            )
            import supabase
            
            data_source = get_data_source()
            if data_source != "supabase":
                logger.info("Supabase no configurado como fuente de datos")
                return []
                
            supabase_url = get_supabase_url()
            supabase_key = get_supabase_key()
            
            if not supabase_url or not supabase_key:
                logger.warning("Credenciales de Supabase no configuradas")
                return []
            
            supabase_client = supabase.create_client(supabase_url, supabase_key)
            
            analisis_table = get_analisis_table()
            result = (
                supabase_client
                .table(analisis_table)
                .select("*")
                .order("fecha_analisis", desc=True)
                .limit(limit)
                .execute()
            )
            
            historial = []
            for record in result.data:
                historial.append({
                    "id": record['id'],
                    "fecha_analisis": record['fecha_analisis'],
                    "nombre_archivo": record['nombre_archivo'],
                    "total_citas": record['total_citas'],
                    "costo_total": record['costo_total'],
                    "resumen": json.loads(record['datos_resumen']) if record['datos_resumen'] else {},
                    "creado_en": record['creado_en']
                })
            
            return historial
        except ImportError:
            logger.warning("Supabase no instalado")
            return []
        except Exception as e:
            logger.error(f"Error al obtener historial de análisis: {str(e)}")
            return []
