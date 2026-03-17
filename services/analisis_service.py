"""
Service for analyzing medical appointments and calculating costs
"""
from typing import List, Dict, Any, Optional

# Import models locally to avoid circular imports
from models.base_model import CitaMedica

class AnalisisService:
    """Service for analyzing medical appointments and calculating costs"""

    def __init__(self, penalizacion_default: float = 20.0):
        self.penalizacion_default = float(penalizacion_default)

    @staticmethod
    def _calcular_monto(cita: CitaMedica, penalizacion: float) -> float:
        return penalizacion if cita.genera_costo() else 0.0
    
    def calcular_costos(self, citas: List[CitaMedica], penalizacion: Optional[float] = None) -> Dict[str, Any]:
        """Calcular costos y generar reportes"""
        if penalizacion is None:
            penalizacion = self.penalizacion_default

        penalizacion = max(float(penalizacion), 0.0)

        costo_total = 0.0
        citas_con_costo = []
        costos_por_empleado = {}
        
        for cita in citas:
            costo = self._calcular_monto(cita, penalizacion)
            costo_total += costo
            
            if costo > 0:
                citas_con_costo.append(cita)
                
                # Acumular por empleado
                emp_nombre = cita.nombre_empleado
                costos_por_empleado[emp_nombre] = costos_por_empleado.get(emp_nombre, 0) + costo

        total_citas = len(citas)
        citas_asistidas = sum(1 for c in citas if c.asistio())
        perdidas_no_anuladas = sum(1 for c in citas if c.genera_costo())
        anuladas = sum(1 for c in citas if c.fue_anulada())
        perdidas_y_anuladas = sum(1 for c in citas if not c.asistio() and c.fue_anulada())

        top_empleados = sorted(
            costos_por_empleado.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        
        return {
            'costo_total': costo_total,
            'penalizacion_aplicada': penalizacion,
            'citas_con_costo': citas_con_costo,
            'costos_por_empleado': costos_por_empleado,
            'top_empleados': top_empleados,
            'resumen': {
                'total_citas': total_citas,
                'asistidas': citas_asistidas,
                'perdidas_no_anuladas': perdidas_no_anuladas,
                'anuladas': anuladas,
                'perdidas_y_anuladas': perdidas_y_anuladas,
                'porcentaje_asistencia': (citas_asistidas / total_citas * 100) if total_citas else 0.0,
                'porcentaje_perdidas': (perdidas_no_anuladas / total_citas * 100) if total_citas else 0.0,
            }
        }
