# MedConnectCo ⚕️

**Sistema de interconexión de historias clínicas electrónicas entre instituciones de salud colombianas.**

Plataforma web construida con arquitectura de **microservicios** que conecta hospitales y clínicas en una red segura para registrar, consultar y compartir historias clínicas digitales en tiempo real, garantizando confidencialidad, trazabilidad y cumplimiento normativo colombiano.

---

## 👥 Integrantes

| Nombre | Rol |
|--------|-----|
| Juan Sebastian Tobon Restrepo | Desarrollador / Arquitecto |
| Diego Sierra Gomez | Desarrollador / Arquitecto |
| Juan Camilo Muñoz Arboleda | Desarrollador / Arquitecto |

---

## 🏗️ Estilo Arquitectónico

**Microservicios** con API Gateway — El sistema está descompuesto en 6 servicios independientes + 1 gateway, cada uno con su propia base de datos SQLite, comunicándose mediante APIs REST y autenticación JWT compartida.

### ¿Por qué microservicios?

- **Escalabilidad independiente**: cada servicio escala según su demanda.
- **Aislamiento de fallos**: si un servicio cae (ej. notificaciones), el resto sigue operando.
- **Independencia en desarrollo**: equipos pueden trabajar en servicios separados.
- **Preparación para producción**: migración natural hacia contenedores Docker y orquestación.

---

## 📦 Estructura del Proyecto

```
MedConnectCo/
├── microservices/                  # ← Arquitectura principal (microservicios)
│   ├── gateway/                    # API Gateway — punto único de entrada
│   │   └── main.py
│   ├── auth_service/               # Servicio de Autenticación (JWT + bcrypt)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── hospital_service/           # Servicio de Hospitales (CRUD + aprobación)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── patient_service/            # Servicio de Pacientes (registro + consentimiento)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── ehr_service/                # Servicio de Historias Clínicas (CRUD + PDF)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── pdf_generator.py
│   ├── audit_service/              # Servicio de Auditoría (logs inmutables)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── notification_service/       # Servicio de Notificaciones
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   └── common/
│       └── security.py             # Módulo compartido de seguridad (JWT + bcrypt)
│
├── frontend/                       # SPA (Single Page Application)
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── legacy_monolith/                # Versión monolítica original (referencia)
│   └── backend/
│
├── entregables/                    # Documentos académicos (Evaluaciones 2, 3, Arquitectura)
├── docs/                           # Documentación adicional
│
├── run_microservices.py            # Script para levantar todos los servicios
├── seed_microservices.py           # Script para poblar las bases de datos
├── requirements.txt                # Dependencias Python
└── README.md
```

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|------------|
| Backend (Microservicios) | Python 3.10+ · FastAPI |
| ORM | SQLAlchemy 2.0 |
| Base de Datos | SQLite (una BD por microservicio) |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| API Gateway | FastAPI + httpx (proxy reverso) |
| Frontend | HTML5 + CSS3 + JavaScript Vanilla (SPA) |
| Generación de PDFs | ReportLab |
| Servidor | Uvicorn (ASGI) |

---

## 🎯 Épicas / MVP Implementadas

### Épica 1 — Gestión de Instituciones de Salud
- ✅ Registro de hospitales con nombre y dirección
- ✅ Aprobación/rechazo de hospitales por el administrador
- ✅ Solo hospitales aprobados operan en la red

### Épica 2 — Gestión de Usuarios y Roles (RBAC)
- ✅ Autenticación con JWT (login/registro)
- ✅ Roles: `admin`, `admin_clinica`, `medico`, `paciente`
- ✅ Admin del sistema: gestión global
- ✅ Admin de clínica: gestión de médicos de su hospital
- ✅ Médicos: CRUD de historias clínicas

### Épica 3 — Historias Clínicas Electrónicas
- ✅ Creación de historias clínicas por médicos autorizados
- ✅ Consulta por documento del paciente
- ✅ Generación automática de PDF de la historia clínica
- ✅ Verificación de existencia del paciente (comunicación inter-servicios)

### Épica 4 — Registro de Pacientes con Consentimiento
- ✅ Registro de pacientes con datos personales
- ✅ Consentimiento informado obligatorio
- ✅ PIN de acceso de 4 dígitos para pacientes
- ✅ Registro de condiciones crónicas (antecedentes)

### Épica 5 — Auditoría y Trazabilidad
- ✅ Registro automático de todas las operaciones críticas
- ✅ Log inmutable con usuario, acción, recurso y detalle
- ✅ Consulta de auditoría solo por administradores

### Épica 6 — Notificaciones
- ✅ Notificaciones automáticas al paciente al crear historia clínica
- ✅ Bandeja de notificaciones por usuario
- ✅ Marcado de notificaciones como leídas

---

## 🧩 Patrones GoF Implementados

| Patrón | Tipo | Ubicación | Descripción |
|--------|------|-----------|-------------|
| **Proxy** | Estructural | `gateway/main.py` → `proxy_request()` | El API Gateway actúa como proxy reverso, interceptando todas las peticiones del frontend y reenviándolas al microservicio correspondiente. |
| **Facade** | Estructural | `gateway/main.py` | El Gateway ofrece una interfaz unificada (puerto 8000) que oculta la complejidad de los 6 microservicios internos al frontend. |
| **Observer** | Comportamental | `ehr_service/main.py` → `create_history()` | Al crear una historia clínica, el servicio notifica asincrónicamente al Audit Service y al Notification Service sin acoplamiento directo. |
| **Strategy** | Comportamental | `common/security.py` → `CryptContext(schemes=["bcrypt"])` | El contexto criptográfico permite intercambiar algoritmos de hashing sin modificar la lógica de autenticación. |
| **Repository** | Arquitectural | Cada microservicio (`database.py` + `models.py`) | Cada servicio encapsula el acceso a su propia base de datos detrás de una capa de abstracción SQLAlchemy. |
| **Adapter** | Estructural | `ehr_service/pdf_generator.py` | Adapta los datos del dominio interno al formato requerido por ReportLab para generar PDFs estandarizados de historias clínicas. |

---

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python **3.10+**
- pip

### 1. Clonar el repositorio
```bash
git clone https://github.com/dsg18/MedconnectCO.git
cd MedconnectCO
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Poblar las bases de datos
```bash
python seed_microservices.py
```

### 4. Levantar todos los microservicios
```bash
python run_microservices.py
```

Esto arranca los 7 procesos (6 servicios + gateway) automáticamente.

### 5. Acceder a la aplicación
| Recurso | URL |
|---------|-----|
| **Frontend (UI)** | http://localhost:8000 |
| **API Gateway** | http://localhost:8000 |
| Auth Service | http://localhost:8001 |
| Hospital Service | http://localhost:8002 |
| Patient Service | http://localhost:8003 |
| EHR Service | http://localhost:8004 |
| Audit Service | http://localhost:8005 |
| Notification Service | http://localhost:8006 |

### 6. Detener los servicios
Presionar `CTRL+C` en la terminal donde se ejecutó `run_microservices.py`.

---

## 🔐 Credenciales de Prueba

| Usuario | Contraseña | Rol | Hospital |
|---------|------------|-----|----------|
| `admin` | `admin123` | Administrador del sistema | — |
| `admin_medellin` | `clinica123` | Administrador de clínica | Hospital General de Medellín |
| `dr_perez` | `medico123` | Médico | Hospital General de Medellín |
| `10203040` | `1234` | Paciente | — |
| `50607080` | `4321` | Paciente | — |

---

## 📡 Arquitectura de Comunicación

```
                    ┌─────────────┐
                    │  Frontend   │
                    │  (SPA)      │
                    └──────┬──────┘
                           │ HTTP :8000
                    ┌──────▼──────┐
                    │ API Gateway │
                    │  (FastAPI)  │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┬───────┐
           │       │       │       │       │       │
      ┌────▼──┐┌───▼───┐┌──▼──┐┌───▼───┐┌──▼──┐┌──▼───┐
      │ Auth  ││ Hosp. ││ Pat.││  EHR  ││Audit││Notif.│
      │ :8001 ││ :8002 ││:8003││ :8004 ││:8005││:8006 │
      └───┬───┘└───┬───┘└──┬──┘└───┬───┘└──┬──┘└──┬───┘
          │        │       │       │       │      │
      [auth.db][hosp.db][pat.db][ehr.db][audit.db][notif.db]
```

---

## 📋 Reglas de Negocio

1. **Aprobación de hospitales**: solo hospitales aprobados por el admin pueden operar en la red.
2. **Control de acceso (RBAC)**: cada rol tiene permisos diferenciados sobre los recursos.
3. **Consentimiento informado**: obligatorio para registrar pacientes.
4. **Auditoría automática**: toda operación crítica queda registrada.
5. **Aislamiento de datos**: cada microservicio tiene su propia base de datos.

---

## ⚠️ Limitaciones y Mejoras Futuras

| Limitación actual | Mejora propuesta |
|-------------------|------------------|
| SQLite por servicio | Migrar a PostgreSQL en producción |
| Sin contenedores | Dockerizar cada microservicio |
| Sin orquestador | Usar Docker Compose / Kubernetes |
| Comunicación HTTP síncrona | Implementar colas de mensajes (RabbitMQ/Kafka) |
| Sin cifrado de datos en reposo | Implementar AES-256 para campos sensibles |
| Sin HTTPS | Configurar TLS en producción |

---

## 📚 Bibliografía

- Bass, L., Clements, P., & Kazman, R. (2021). *Software architecture in practice* (4.a ed.). Addison-Wesley.
- Newman, S. (2019). *Building microservices: Designing fine-grained systems* (2.a ed.). O'Reilly Media.
- Richardson, C. (2018). *Microservices patterns: With examples in Java*. Manning Publications.
- Brown, S. (2018). *The C4 model for visualising software architecture*. https://c4model.com/
- Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley.
- Fowler, M. (2002). *Patterns of enterprise application architecture*. Addison-Wesley.
