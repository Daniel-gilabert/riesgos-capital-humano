"""
Data Service for loading and preparing data for analysis
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DataService:
    """Service for loading and preparing data"""
    
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
        
        # Leer el archivo Excel
        df = pd.read_excel(archivo_subido)
        
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
        for _, fila in df.iterrows():
            try:
                cita = CitaMedica(
                    nombre_empleado=str(fila[mapeo_columnas['persona trabajadora']]).strip(),
                    fecha_cita=pd.to_datetime(fila[mapeo_columnas['fecha']]),
                    asistencia=str(fila[mapeo_columnas['asistencia']]).strip(),
                    anulada=str(fila[mapeo_columnas['anulada']]).strip()
                )
                citas.append(cita)
            except Exception as e:
                logger.warning(f"Error procesando fila: {fila}. Error: {e}")
                continue
        
        return citas
    
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
            from config import get_data_source, get_supabase_url, get_supabase_key
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
            
            # Insertar en tabla analisis
            result = supabase_client.table("analisis").insert(analisis_data).execute()
            
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
                supabase_client.table("citas_analizadas").insert(citas_data).execute()
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
            from config import get_data_source, get_supabase_url, get_supabase_key
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
            
            result = supabase_client.table("analisis").select("*").order("fecha_analisis", desc=True).limit(limit).execute()
            
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