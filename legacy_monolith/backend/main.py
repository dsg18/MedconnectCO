from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import engine, Base
from .auth_service import router as auth_router
from .routers.hospitales import router as hospitales_router
from .routers.pacientes import router as pacientes_router
from .routers.historias import router as historias_router
from .routers.usuarios import router as usuarios_router

# Crea todas las tablas al iniciar (SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedConnectCo",
    description=(
        "Plataforma que conecta instituciones de salud colombianas en una red segura "
        "para registrar y consultar historias clínicas digitales en tiempo real."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(hospitales_router)
app.include_router(pacientes_router)
app.include_router(historias_router)
app.include_router(usuarios_router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "mensaje": "MedConnectCo - API activa"}


# ── Frontend estático ─────────────────────────────────────────────────────────
_frontend = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(_frontend):
    app.mount("/app", StaticFiles(directory=_frontend, html=True), name="frontend")
