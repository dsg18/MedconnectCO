from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Hospital ──────────────────────────────────────────────────────────────────

class HospitalBase(BaseModel):
    nombre: str
    direccion: str

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    id: int
    aprobado: bool

    class Config:
        orm_mode = True


# ── Usuario ───────────────────────────────────────────────────────────────────

class UsuarioBase(BaseModel):
    username: str
    rol: str
    hospital_id: Optional[int] = None
    creado_por: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True


# ── Paciente ──────────────────────────────────────────────────────────────────

class PacienteBase(BaseModel):
    documento: str
    nombre_completo: str

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: int

    class Config:
        orm_mode = True


# ── Historia Clínica ──────────────────────────────────────────────────────────

class HistoriaClinicaBase(BaseModel):
    diagnostico: str
    tratamiento: str

class HistoriaClinicaCreate(HistoriaClinicaBase):
    paciente_documento: str

class HistoriaClinica(HistoriaClinicaBase):
    id: int
    fecha_creacion: datetime
    paciente_id: int
    medico_id: int
    pdf_path: Optional[str] = None

    class Config:
        orm_mode = True


# ── Vistas compuestas ─────────────────────────────────────────────────────────

class PacienteDetalle(Paciente):
    """Paciente con todas sus historias clínicas incluidas."""
    historias: List[HistoriaClinica] = []

    class Config:
        orm_mode = True


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
