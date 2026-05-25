from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Hospital(Base):
    __tablename__ = "hospitales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    direccion = Column(String)
    aprobado = Column(Boolean, default=False)
