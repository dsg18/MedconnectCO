from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HistoriaClinicaBase(BaseModel):
    diagnostico: str
    tratamiento: str

class HistoriaClinicaCreate(HistoriaClinicaBase):
    paciente_documento: str

class HistoriaClinica(HistoriaClinicaBase):
    id: int
    fecha_creacion: datetime
    paciente_documento: str
    medico_id: int
    hospital_id: int
    pdf_path: Optional[str] = None
    class Config: orm_mode = True
