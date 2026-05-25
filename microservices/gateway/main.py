from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="MedConnectCo Gateway")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los Microservicios
SERVICES = {
    "auth":      "http://localhost:8001",
    "hospitales": "http://localhost:8002",
    "pacientes":  "http://localhost:8003",
    "historias":  "http://localhost:8004",
    "auditoria":  "http://localhost:8005",
    "notificaciones": "http://localhost:8006",
}

async def proxy_request(service_url: str, path: str, request: Request):
    url = f"{service_url}/{path}"
    async with httpx.AsyncClient() as client:
        # Reenviar headers, query params y body
        method = request.method
        content = await request.body()
        headers = dict(request.headers)
        # Eliminar host para evitar problemas de proxy
        headers.pop("host", None)
        
        resp = await client.request(
            method,
            url,
            content=content,
            params=request.query_params,
            headers=headers,
            timeout=10.0
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def auth_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["auth"], path, request)

@app.api_route("/hospitales/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def hospitals_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["hospitales"], path, request)

@app.api_route("/pacientes/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def patients_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["pacientes"], path, request)

@app.api_route("/usuarios/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def users_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["auth"], path, request)

@app.api_route("/historias/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def ehr_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["historias"], path, request)

@app.api_route("/auditoria/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def audit_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["auditoria"], path, request)

@app.api_route("/notificaciones/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def notification_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["notificaciones"], path, request)

# Rutas absolutas para evitar problemas de dirección
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
PDF_PATH = os.path.join(BASE_DIR, "microservices", "ehr_service", "static", "pdfs")

os.makedirs(PDF_PATH, exist_ok=True)

# Mount de PDFs en /historia_pdfs
app.mount("/historia_pdfs", StaticFiles(directory=PDF_PATH), name="pdfs")

# Servir el Frontend y sus archivos estáticos en la raíz
# IMPORTANTE: Esto debe ir al final para no interferir con las rutas /auth, /hospitales, etc.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
