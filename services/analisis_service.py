"""
Service for analyzing medical appointments and calculating costs
"""
from typing import List, Dict, Any

# Import models locally to avoid circular imports
from models.base_model import CitaMedica

class AnalisisService:
    """Service for analyzing medical appointments and calculating costs"""
    
    def calcular_costos(self, citas: List[CitaMedica]) -> Dict[str, Any]:
        """Calcular costos y generar reportes"""
        costo_total = 0.0
        citas_con_costo = []
        costos_por_empleado = {}
        
        for cita in citas:
            costo = cita.obtener_monto_costo()
            costo_total += costo
            
            if costo > 0:
                citas_con_costo.append(cita)
                
                # Acumular por empleado
                emp_nombre = cita.nombre_empleado
                costos_por_empleado[emp_nombre] = costos_por_empleado.get(emp_nombre, 0) + costo
        
        return {
            'costo_total': costo_total,
            'citas_con_costo': citas_con_costo,
            'costos_por_empleado': costos_por_empleado,
            'resumen': {
                'total_citas': len(citas),
                'asistidas': sum(1 for c in citas if c.asistio()),
                'perdidas_no_anuladas': sum(1 for c in citas if c.genera_costo()),
                'anuladas': sum(1 for c in citas if c.fue_anulada()),
                'perdidas_y_anuladas': sum(1 for c in citas if not c.asistio() and c.fue_anulada())
            }
        }