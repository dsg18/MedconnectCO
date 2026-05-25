from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    usuario: str
    mensaje: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    leido: bool
    timestamp: datetime

    class Config:
        orm_mode = True
