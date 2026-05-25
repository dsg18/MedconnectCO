from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ESTA CLAVE DEBE SER LA MISMA EN TODOS LOS MICROSERVICIOS
SECRET_KEY = "medconnectco_super_secret_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_data(auth: HTTPAuthorizationCredentials = Security(security)):
    """
    Valida el token y devuelve los datos del usuario.
    En microservicios, cada servicio valida el token de forma independiente
    usando la misma SECRET_KEY.
    """
    payload = decode_token(auth.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    payload["token_original"] = auth.credentials
    return payload
