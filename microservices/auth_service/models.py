from sqlalchemy import Column, Integer, String
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String) # admin, admin_clinica, medico
    hospital_id = Column(Integer, nullable=True) # ID lógico
    creado_por = Column(String, nullable=True)
