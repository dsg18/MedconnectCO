from pydantic import BaseModel
from typing import Optional

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

class Token(BaseModel):
    access_token: str
    token_type: str
