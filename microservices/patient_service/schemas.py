from pydantic import BaseModel
from typing import Optional, List

class CondicionCronicaBase(BaseModel):
    nombre: str
    fecha_diagnostico: str

class CondicionCronicaCreate(CondicionCronicaBase):
    pass

class CondicionCronica(CondicionCronicaBase):
    id: int
    class Config: orm_mode = True

class PacienteBase(BaseModel):
    documento: str
    nombre_completo: str
    fecha_expedicion: str
    fecha_nacimiento: str
    consentimiento: bool = False

class PacienteCreate(PacienteBase):
    pin: str 

class Paciente(PacienteBase):
    id: int
    condiciones: List[CondicionCronica] = [] # Incluimos la lista de condiciones
    class Config: orm_mode = True
