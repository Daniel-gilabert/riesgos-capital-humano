"""
Data Service for loading and preparing data for analysis
"""
import pandas as pd
import numpy as np
from typing import Optional, List
import logging

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