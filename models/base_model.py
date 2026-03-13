from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

@dataclass
class BaseModel:
    """Base model for all entities"""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        # Handle datetime fields
        datetime_fields = ['created_at', 'updated_at']
        for field in datetime_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])
        return cls(**data)

@dataclass
class RiskFactor(BaseModel):
    """Model for a risk factor in human capital"""
    name: str = field(default="")
    description: str = field(default="")
    category: str = field(default="")  # e.g., 'Recruitment', 'Retention', 'Performance', 'Culture'
    severity: str = field(default="")  # e.g., 'Low', 'Medium', 'High', 'Critical'
    probability: str = field(default="")  # e.g., 'Unlikely', 'Possible', 'Likely', 'Almost Certain'
    department: Optional[str] = field(default=None)
    location: Optional[str] = field(default=None)
    detected_date: Optional[datetime] = field(default=None)
    mitigation_plan: Optional[str] = field(default=None)
    owner: Optional[str] = field(default=None)  # Person responsible for mitigation
    status: str = field(default="Identified")  # Identified, In Mitigation, Mitigated, Accepted
    impact_score: int = field(default=0)  # 1-5 scale
    likelihood_score: int = field(default=0)  # 1-5 scale
    risk_score: int = field(default=0)  # Calculated as impact * likelihood
    
    def calculate_risk_score(self) -> int:
        """Calculate risk score based on impact and likelihood"""
        if self.impact_score > 0 and self.likelihood_score > 0:
            self.risk_score = self.impact_score * self.likelihood_score
        return self.risk_score
    
    def get_risk_level(self) -> str:
        """Get risk level based on score"""
        score = self.calculate_risk_score()
        if score >= 15:
            return "Critical"
        elif score >= 10:
            return "High"
        elif score >= 5:
            return "Medium"
        else:
            return "Low"

@dataclass
class CitaMedica(BaseModel):
    """Modelo para registros de citas médicas"""
    nombre_empleado: str = field(default="")  # persona trabajadora
    fecha_cita: Optional[datetime] = field(default=None)  # fecha (incluye fecha y hora)
    asistencia: str = field(default="")       # "Sí" o "No"
    anulada: str = field(default="")          # "Sí" o "No"
    
    def asistio(self) -> bool:
        return self.asistencia.strip().lower() == "sí"
    
    def fue_anulada(self) -> bool:
        return self.anulada.strip().lower() == "sí"
    
    def genera_costo(self) -> bool:
        """Retorna True si esta cita genera un costo (20€ de penalización)"""
        # Costo ocurre cuando: NO asistió Y NO fue anulada
        return not self.asistio() and not self.fue_anulada()
    
    def obtener_monto_costo(self) -> float:
        """Retorna el monto de costo para esta cita"""
        return 20.0 if self.genera_costo() else 0.0

@dataclass
class EmployeeData(BaseModel):
    """Model for employee data used in risk analysis"""
    employee_id: str = field(default="")
    name: str = field(default="")
    department: str = field(default="")
    position: str = field(default="")
    hire_date: Optional[datetime] = field(default=None)
    salary: Optional[float] = field(default=None)
    performance_score: Optional[float] = field(default=None)  # 1-5 scale
    engagement_score: Optional[float] = field(default=None)  # 1-5 scale
    absenteeism_days: int = field(default=0)
    overtime_hours: float = field(default=0.0)
    training_hours: float = field(default=0.0)
    promotion_eligible: bool = field(default=False)
    flight_risk_score: Optional[float] = field(default=None)  # 0-1 scale