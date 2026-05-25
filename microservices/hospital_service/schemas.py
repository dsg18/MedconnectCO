from pydantic import BaseModel

class HospitalBase(BaseModel):
    nombre: str
    direccion: str

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    id: int
    aprobado: bool
    class Config: orm_mode = True
