# MedConnectCo — Documento Final Consolidado
## Proyecto Final de Arquitectura de Software — 2026-1

---

**Integrantes:**
- Juan Sebastian Tobón Restrepo
- Diego Sierra Gómez
- Juan Camilo Muñoz Arboleda

**Asignatura:** Arquitectura de Datos  
**Fecha:** Mayo 2026

---

## Tabla de Contenido

1. Contexto del Sistema
2. Actores Principales
3. Restricciones Relevantes
4. Historias de Usuario
5. Requisitos Funcionales
6. Requisitos No Funcionales
7. Atributos de Calidad
8. Estilo Arquitectónico — Justificación
9. Modelo C4 — Diagramas de Arquitectura
10. Patrones GoF Implementados
11. Decisiones Arquitectónicas
12. MVP Implementado
13. Riesgos, Limitaciones y Mejoras Futuras
14. Declaración de Uso de IA
15. Bibliografía

---

## 1. Contexto del Sistema

### 1.1 Descripción del Problema

En Colombia, los hospitales y centros médicos operan con sistemas de información aislados. No existe una red nacional unificada para compartir historias clínicas digitales de manera segura y estandarizada.

**Necesidad principal:** Implementar una plataforma web que conecte a las instituciones de salud en una red segura, permitiendo registrar y consultar historias clínicas digitales en tiempo real. De esta manera, los profesionales de la salud podrán acceder a información completa y actualizada del paciente, garantizando confidencialidad y cumplimiento normativo.

**Impacto esperado:**
- Mejora en continuidad del tratamiento médico
- Reducción de errores médicos por falta de información
- Optimización del tiempo de atención
- Seguridad y trazabilidad de la información clínica
- Interoperabilidad entre instituciones

---

## 2. Actores Principales

| Actor | Descripción | Tipo |
|-------|-------------|------|
| **Administrador del sistema** | Gestiona la plataforma a nivel general, valida el registro de hospitales, asigna permisos y supervisa la seguridad y funcionamiento del sistema | Interno |
| **Administrador por clínica** | Representante de cada hospital, encargado de gestionar usuarios internos (médicos y personal autorizado) y administrar la información de la clínica | Interno |
| **Médicos** | Se encarga de crear, actualizar y consultar historias clínicas de los pacientes | Interno |
| **Paciente** | Persona cuya información médica es almacenada por parte de los médicos, y puede ser consultada por los mismos. Otorga consentimiento informado | Externo |

---

## 3. Restricciones Relevantes

| Restricción | Descripción |
|-------------|-------------|
| Regulación colombiana | Cumplimiento con la Resolución 1995 de 1999 (manejo de historia clínica) y Ley 1581 de 2012 (protección de datos personales) |
| Seguridad | Toda información médica debe estar protegida mediante cifrado y acceso con usuario y contraseña segura |
| Disponibilidad | El sistema debe estar disponible la mayor parte del tiempo (mínimo 99%) para garantizar acceso continuo |
| Rendimiento | Las consultas de historia clínica deben cargar en máximo 3 segundos en condiciones normales |
| Trazabilidad | Cada vez que alguien consulte o modifique una historia clínica, el sistema debe guardar registro de quién lo hizo y cuándo |

---

## 4. Historias de Usuario

### HU-01 — Registro y Validación de Instituciones de Salud

*Como administrador del sistema, quiero poder registrar y validar hospitales y clínicas en la plataforma, para garantizar que solo instituciones verificadas accedan a la red nacional de historias clínicas.*

**Criterios de aceptación:**
- Dado que una institución desea unirse a la plataforma, cuando presenta la documentación y datos requeridos para su registro, entonces el sistema valida la información y activa la institución únicamente tras aprobación explícita del administrador del sistema.
- El sistema debe notificar a la institución sobre el estado de su solicitud (aprobada, rechazada o pendiente de información adicional).
- Solo las instituciones con estado 'activo' pueden operar dentro de la red.

### HU-02 — Creación de Historia Clínica

*Como médico autenticado en la plataforma, quiero crear y registrar la historia clínica de un paciente, para garantizar que su información médica quede almacenada de forma segura y estructurada.*

**Criterios de aceptación:**
- Dado que el médico ha iniciado sesión en el sistema con sus credenciales institucionales, cuando registra los datos clínicos requeridos del paciente (datos personales, diagnóstico, tratamiento, etc.), entonces el sistema almacena la información en la base de datos de forma cifrada y asociada al identificador único del paciente.
- El sistema debe confirmar el guardado exitoso mediante una notificación al médico.
- Toda creación o modificación queda registrada en el log de auditoría con fecha, hora y usuario responsable.

### HU-03 — Consulta Interinstitucional de Historias Clínicas

*Como médico perteneciente a una institución registrada, quiero poder consultar la historia clínica de un paciente atendido previamente en otra institución, para garantizar la continuidad del tratamiento y tomar decisiones clínicas informadas.*

**Criterios de aceptación:**
- Dado que el médico pertenece a una institución activa en la red, cuando realiza una búsqueda por el número de documento del paciente, entonces el sistema muestra el historial clínico completo disponible, organizado cronológicamente y de forma comprensible.
- El acceso a la historia clínica de un paciente en otra institución queda registrado en el log de auditoría.
- Solo el personal médico autorizado puede realizar consultas interinstitucionales.

---

## 5. Requisitos Funcionales

| ID | Requisito Funcional | HU | Prioridad | Impacto Arquitectónico |
|----|---------------------|----|-----------|------------------------|
| RF-01 | El sistema debe permitir registrar, aprobar y activar instituciones de salud en la plataforma | HU-01 | Alta | Módulo de validación con estados de ciclo de vida institucional |
| RF-02 | El sistema debe permitir gestionar usuarios y roles por institución, con acceso diferenciado según perfil | HU-01, HU-02 | Alta | Control de acceso basado en roles (RBAC) y gestión de sesiones |
| RF-03 | El sistema debe permitir crear, actualizar y consultar historias clínicas digitales de manera segura | HU-02, HU-03 | Alta | Almacenamiento estructurado y cifrado, APIs de consulta optimizadas |
| RF-04 | El sistema debe permitir al paciente autorizar el acceso a su información y consultar quién ha accedido a sus datos | HU-03 | Alta | Módulo de gestión de consentimiento y sistema de trazabilidad de accesos |

---

## 6. Requisitos No Funcionales

| ID | Requisito | Atributo | Métrica | Justificación |
|----|-----------|----------|---------|---------------|
| RNF-01 | Seguridad de la información clínica | Seguridad | 100% de datos cifrados en tránsito (HTTPS/TLS) y en reposo (AES-256) | Los datos clínicos son altamente sensibles. Su compromiso implica riesgos legales, éticos y de seguridad |
| RNF-02 | Disponibilidad continua del sistema | Disponibilidad | ≥ 99% de disponibilidad mensual (máx. 7.2 horas de inactividad/mes) | El sistema debe estar disponible en todo momento para garantizar la atención médica ininterrumpida |
| RNF-03 | Rendimiento en consultas clínicas | Rendimiento | Tiempo de respuesta ≤ 3 segundos en consultas estándar bajo carga normal | Un sistema lento en entornos clínicos puede comprometer la atención al paciente en urgencias |
| RNF-04 | Auditabilidad y registro de accesos | Auditabilidad | 100% de accesos registrados con usuario, fecha, hora e institución de origen | Requisito legal y ético para garantizar la trazabilidad de quién accede a información sensible |

---

## 7. Atributos de Calidad

| Atributo | Justificación | Prioridad | Impacto en Arquitectura |
|----------|---------------|-----------|-------------------------|
| **Seguridad** | Los datos médicos son extremadamente sensibles. Una brecha puede comprometer la privacidad y generar sanciones legales | Crítica | Autenticación JWT, cifrado bcrypt, RBAC, auditoría completa |
| **Auditabilidad** | Requisito legal (Resolución 1995/99). Todo acceso debe quedar registrado | Crítica | Servicio de auditoría independiente con logs inmutables |
| **Disponibilidad** | El sistema debe funcionar 24/7 para hospitales de todo el país | Alta | Microservicios con aislamiento de fallos |
| **Rendimiento** | Consultas deben ser rápidas en situaciones de urgencia médica | Alta | API Gateway como proxy reverso, bases de datos por servicio |
| **Interoperabilidad** | Múltiples instituciones con diferentes sistemas deben poder conectarse | Alta | APIs REST estándar, esquemas Pydantic compatibles con HL7 FHIR |
| **Escalabilidad** | La red debe crecer a nivel nacional con cientos de instituciones | Alta | Arquitectura de microservicios con escalabilidad horizontal |

---

## 8. Estilo Arquitectónico — Justificación

### Estilo elegido: Microservicios con API Gateway

El estilo arquitectónico adoptado es el de **microservicios**, implementado bajo una estrategia de **descomposición modular progresiva**. Esta decisión responde a la necesidad de diseñar un sistema distribuido robusto que garantice la integración efectiva y el intercambio de datos entre múltiples instituciones hospitalarias a nivel nacional.

Se eligió este estilo porque tiene la habilidad de descomponer el sistema en elementos funcionales independientes y autónomos, lo que hace más fácil la escalabilidad, el mantenimiento y el desarrollo gradual del sistema conforme aumenta y se expande la red de instituciones conectadas.

### Justificación técnica

Dado que el sistema necesita interoperabilidad entre diversas entidades de salud, la selección de una arquitectura basada en microservicios es apropiada. Este método posibilita la separación de funciones esenciales como la gestión de identidades, el registro de las historias clínicas y los módulos de autenticación, asegurando que cada dominio evolucione sin comprometer la integridad global del sistema.

El empleo de microservicios favorece la autonomía en el ciclo de vida de cada componente, reduciendo significativamente el radio de impacto ante fallos y facilitando la adopción de prácticas de integración y entrega continua (CI/CD).

### Fortalezas del estilo elegido

1. **Escalabilidad independiente**: cada servicio puede escalar horizontalmente según su demanda sin afectar a los demás.
2. **Aislamiento de fallos**: si un servicio falla, el resto del sistema continúa operando.
3. **Autonomía de datos**: cada servicio tiene su propia base de datos, evitando cuellos de botella.
4. **Tecnología heterogénea**: cada servicio puede usar la tecnología más adecuada para su dominio.
5. **Despliegue independiente**: actualizaciones sin necesidad de redesplegar todo el sistema.

### Limitaciones reconocidas

1. **Complejidad operacional**: 7 procesos en lugar de 1, requiere orquestación.
2. **Consistencia eventual**: sin transacciones distribuidas entre servicios.
3. **Latencia adicional**: comunicación HTTP entre servicios añade overhead.
4. **Monitoreo distribuido**: requiere herramientas especializadas para rastrear flujos.

---

## 9. Modelo C4 — Diagramas de Arquitectura

> **Nota:** Los diagramas completos en formato visual se encuentran en el documento *MedConnectCO.Arquitectura.docx.pdf* incluido en la carpeta `entregables/`. A continuación se presenta la descripción técnica de cada nivel.

### 9.1 C1 — Diagrama de Contexto

El diagrama de contexto muestra MedConnectCO como una caja negra y su relación con los actores externos.

| Elemento | Descripción |
|----------|-------------|
| Paciente | Actor principal. Propietario legal de la HCE. Autoriza el acceso mediante consentimiento digital |
| Profesional de Salud | Médico, enfermero o especialista que consulta y registra información clínica |
| Administrador | Gestiona la incorporación de instituciones y la configuración de permisos globales |
| MinSalud Colombia | Ente regulador. MedConnectCO envía reportes y cumple normativas |
| Servicio de Notificaciones | Sistema para envío de alertas por correo electrónico y SMS |

### 9.2 C2 — Diagrama de Contenedores

El diagrama descompone MedConnectCO en sus unidades desplegables de forma independiente.

| Contenedor | Tecnología | Responsabilidad | Puerto |
|------------|------------|-----------------|--------|
| Web App (SPA) | HTML5/CSS3/JavaScript | Interfaz de usuario dinámica | — |
| API Gateway | Python (FastAPI) | Punto único de entrada: enrutamiento, autenticación | 8000 |
| Auth Service | Python (FastAPI) | Gestión de identidades, generación de tokens JWT | 8001 |
| Hospital Service | Python (FastAPI) | CRUD de hospitales, aprobación | 8002 |
| Patient Service | Python (FastAPI) | Registro de pacientes, condiciones crónicas, consentimiento | 8003 |
| HCE Service | Python (FastAPI) | Lógica de negocio para gestión de historias clínicas, generación de PDFs | 8004 |
| Audit Service | Python (FastAPI) | Registro inmutable de todas las operaciones del sistema | 8005 |
| Notification Service | Python (FastAPI) | Gestión de notificaciones al paciente | 8006 |
| BD Relacional | SQLite (una por servicio) | Almacenamiento de datos clínicos estructurados | — |

### 9.3 C3 — Diagrama de Componentes del HCE Service

| Componente | Patrón / Tecnología | Función |
|------------|---------------------|---------|
| HCEController | REST Controller | Expone endpoints REST. Recibe solicitudes HTTP y delega en la capa de servicio |
| HCEServiceImpl | Business Logic | Reglas de negocio: validar permisos, coordinar acceso a HCE, garantizar integridad |
| HCERepository | Repository (JPA) | Abstrae el acceso a la base de datos usando el patrón Repository sobre SQLAlchemy |
| HCEMapper | DTO Mapper | Transforma entidades de dominio a DTOs y viceversa |
| HCEValidator | Bean Validation | Valida la integridad y coherencia de los datos clínicos antes de su persistencia |
| PDFGenerator | Adapter | Genera PDFs estandarizados de historias clínicas mediante ReportLab |

### 9.4 C4 — Diagrama de Clases del Dominio

| Clase | Atributos Clave | Descripción |
|-------|-----------------|-------------|
| Paciente | id, nombre, documento, consentimiento, pin | Entidad central del dominio. Propietario de la HCE y otorgante de permisos |
| HistoriaClinica | id, fechaCreacion, diagnóstico, tratamiento, pdf_path | Agregado raíz que agrupa toda la información clínica de un paciente |
| Hospital (Institución) | id, nombre, dirección, aprobado | Entidad hospitalaria registrada en la plataforma |
| Usuario (ProfesionalSalud) | id, username, rol, hospital_id | Profesional habilitado para acceder y registrar información clínica |
| CondicionCronica | id, nombre, fecha_diagnostico | Antecedente médico crónico asociado al paciente |
| AuditLog (AuditoriaAcceso) | id, timestamp, usuario, accion, recurso | Registro inmutable de cada acceso o intento de acceso al sistema |
| Notification | id, usuario, mensaje, leido, timestamp | Notificación enviada al paciente sobre eventos del sistema |

---

## 10. Patrones GoF Implementados

| Patrón | Tipo | Ubicación en código | Descripción |
|--------|------|---------------------|-------------|
| **Proxy** | Estructural | `microservices/gateway/main.py` → función `proxy_request()` | El API Gateway actúa como proxy reverso: intercepta todas las peticiones del frontend y las reenvía al microservicio correspondiente, añadiendo control de routing y headers |
| **Facade** | Estructural | `microservices/gateway/main.py` | El Gateway ofrece una interfaz unificada (puerto 8000) que oculta la complejidad de los 6 microservicios internos. El frontend solo conoce un punto de entrada |
| **Observer** | Comportamental | `microservices/ehr_service/main.py` → función `create_history()` | Al crear una historia clínica, el EHR Service notifica asincrónicamente al Audit Service (registro de auditoría) y al Notification Service (alerta al paciente), sin acoplamiento directo |
| **Strategy** | Comportamental | `microservices/common/security.py` → `CryptContext(schemes=["bcrypt"])` | El contexto criptográfico de passlib permite intercambiar algoritmos de hashing (bcrypt, argon2, etc.) sin modificar la lógica de autenticación. Es una implementación del patrón Strategy |
| **Repository** | Arquitectural | Cada microservicio: `database.py` + `models.py` | Cada servicio encapsula el acceso a su propia base de datos SQLite detrás de una capa de abstracción SQLAlchemy, separando la lógica de negocio del acceso a datos |
| **Adapter** | Estructural | `microservices/ehr_service/pdf_generator.py` | Adapta los datos del modelo de dominio interno al formato requerido por ReportLab para generar PDFs estandarizados de historias clínicas |

---

## 11. Decisiones Arquitectónicas

### 11.1 Beneficios de la arquitectura elegida

- **Separación de responsabilidades**: cada capa maneja exclusivamente la presentación, lógica de negocio, seguridad y acceso a datos.
- **Escalabilidad independiente**: cada componente puede escalar según la demanda sin afectar al otro.
- **Seguridad reforzada**: la comunicación entre capas se realiza exclusivamente a través de APIs REST protegidas con JWT.
- **Preparación para producción**: el diseño modular permite evolucionar hacia contenedores Docker sin reestructuración total.

### 11.2 Trade-offs Identificados

| Decisión | Beneficio | Trade-off |
|----------|-----------|-----------|
| BD por microservicio (SQLite) | Aislamiento total de datos por dominio | No hay joins entre servicios; requiere comunicación HTTP |
| JWT compartido vía common/security.py | Autenticación descentralizada, cada servicio valida tokens | Misma SECRET_KEY en todos los servicios |
| Separación Frontend / Backend | SPA independiente + APIs reutilizables | Mayor complejidad de CORS y configuración |
| SQLite en lugar de PostgreSQL | Simplicidad para desarrollo y demostración | No apto para producción con alta concurrencia |
| Comunicación HTTP síncrona | Implementación simple y directa | Mayor latencia vs. colas de mensajes |

### 11.3 Comparación Monolito vs. Microservicios

El proyecto incluye ambas versiones para evidenciar la migración arquitectónica:

| Aspecto | Monolito (`legacy_monolith/`) | Microservicios (`microservices/`) |
|---------|-------------------------------|-----------------------------------|
| Procesos | 1 | 7 (6 servicios + gateway) |
| Base de datos | 1 SQLite compartida | 6 SQLite independientes |
| Escalabilidad | Vertical | Horizontal (por servicio) |
| Tolerancia a fallos | Todo cae junto | Fallo aislado por servicio |
| Complejidad | Baja | Mayor (justificada) |
| Despliegue | Monolítico | Independiente por servicio |

---

## 12. MVP Implementado

### 12.1 Descripción del MVP

El MVP es una implementación funcional completa del sistema MedConnectCo con arquitectura de microservicios, que demuestra las 6 épicas principales del proyecto.

### 12.2 Tecnologías utilizadas

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

### 12.3 Épicas implementadas

1. **Gestión de Instituciones**: Registro, aprobación y eliminación de hospitales
2. **Gestión de Usuarios (RBAC)**: Autenticación JWT, roles admin/admin_clinica/medico/paciente
3. **Historias Clínicas Electrónicas**: CRUD completo con generación de PDFs
4. **Registro de Pacientes**: Con consentimiento informado, PIN de acceso y condiciones crónicas
5. **Auditoría y Trazabilidad**: Log inmutable de todas las operaciones críticas
6. **Notificaciones**: Alertas automáticas al paciente al crear historias clínicas

### 12.4 Instrucciones de ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Poblar las bases de datos con datos de prueba
python seed_microservices.py

# 3. Levantar todos los microservicios
python run_microservices.py

# Frontend disponible en: http://localhost:8000
```

### 12.5 Enlace al repositorio

**URL del repositorio:** *(Pendiente: subir a GitHub)*

---

## 13. Riesgos, Limitaciones y Mejoras Futuras

### 13.1 Riesgos identificados

| Riesgo | Causa | Impacto | Estrategia de Mitigación |
|--------|-------|---------|--------------------------|
| Fuga o acceso no autorizado a datos médicos | Ataques informáticos, fallas de seguridad o uso indebido por usuarios internos | Alto | Implementar controles de acceso estrictos (RBAC), cifrado, monitoreo de accesos y auditorías periódicas |
| Caídas o interrupciones del sistema | Alta demanda de usuarios, fallas del servidor o problemas de infraestructura | Alto | Diseñar para alta disponibilidad con microservicios aislados, respaldos y monitoreo continuo |
| Resistencia institucional al cambio | Hospitales acostumbrados a sus propios sistemas | Medio | Capacitación, acompañamiento técnico y demostración de beneficios claros con pilotos |
| Errores en la integración con sistemas existentes | Diferencias tecnológicas entre hospitales, formatos incompatibles | Medio-Alto | Definir estándares claros de integración (APIs documentadas, formatos HL7 FHIR) y pruebas piloto |

### 13.2 Limitaciones actuales

| Limitación | Descripción |
|------------|-------------|
| SQLite en desarrollo | No apto para producción con alta concurrencia |
| Sin contenedores Docker | Despliegue manual de cada servicio |
| Sin orquestador | No hay Docker Compose ni Kubernetes |
| Comunicación HTTP síncrona | Mayor latencia vs. colas de mensajes |
| Sin cifrado en reposo | Los datos en las BD SQLite no están cifrados |
| Sin HTTPS | No hay TLS configurado |

### 13.3 Mejoras futuras

- Migrar a **PostgreSQL** en producción
- **Dockerizar** cada microservicio con Docker Compose
- Implementar colas de mensajes (**RabbitMQ / Kafka**) para comunicación asíncrona
- Cifrado **AES-256** para datos en reposo
- Implementar el estándar **HL7 FHIR** para interoperabilidad real
- **HTTPS/TLS** en producción
- Autenticación **multifactor (MFA)**
- **Service mesh** para observabilidad distribuida

---

## 14. Declaración de Uso de Inteligencia Artificial

| Campo | Detalle |
|-------|---------|
| ¿Se utilizó IA generativa? | Sí |
| Herramienta utilizada | Claude (Anthropic) y ChatGPT (OpenAI) |
| Momento en que se usó | Estructuración de documentos, generación de código PlantUML para diagramas C4, proposición de patrones arquitectónicos, apoyo en redacción técnica y generación de código base de microservicios |
| Prompt(s) utilizados | "Con base en los siguientes requisitos de un sistema web de hospitales, apóyame en estructurarlos de manera más técnica, diferenciando funcionales de los no funcionales y agregando métricas donde sea necesario" — "Genera los diagramas C4 en PlantUML para un sistema de historias clínicas con microservicios" |
| Resultado entregado por la IA | Estructuración de requisitos, propuestas de diagramas C4 en PlantUML, sugerencias de patrones GoF, código base de microservicios en FastAPI |
| Qué partes ajustó o corrigió el equipo | Se ajustaron requisitos para coherencia con el alcance real del proyecto. Se redefinieron los requisitos funcionales y no funcionales para alinearlos con el contexto colombiano. Se revisaron y reemplazaron algunas referencias bibliográficas |
| Cómo se validó la información | Comparando conceptos con bibliografía académica (arquitectura de software y estándares de calidad). Verificando que los requisitos cumplieran con características medibles y verificables. Revisando coherencia entre requisitos, atributos de calidad, arquitectura y riesgos |
| Qué limitaciones o errores se detectaron | La IA propuso tecnologías no utilizadas (JPA, MapStruct); se ajustó al stack real. Algunas descripciones eran genéricas y se personalizaron al contexto del proyecto |
| Aporte real de la IA al trabajo | Herramienta de productividad y verificación. No reemplazó el análisis crítico ni la toma de decisiones arquitectónicas del equipo |

---

## 15. Bibliografía

Bass, L., Clements, P., & Kazman, R. (2021). *Software architecture in practice* (4.ª ed.). Addison-Wesley Professional.

Brown, S. (2018). *The C4 model for visualising software architecture*. Leanpub. https://c4model.com/

Congreso de la República de Colombia. (2012). *Ley 1581 de 2012: Régimen general de protección de datos personales*. https://www.funcionpublica.gov.co

European Parliament & Council of the European Union. (2016). *General Data Protection Regulation (GDPR) – Regulation (EU) 2016/679*. https://gdpr-info.eu

Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley Professional.

Fowler, M. (2002). *Patterns of enterprise application architecture*. Addison-Wesley Professional.

Health Level Seven International. (2021). *HL7 FHIR R4 – Fast Healthcare Interoperability Resources*. https://hl7.org/fhir/R4/

Ministerio de Salud y Protección Social de Colombia. (1999). *Resolución 1995 de 1999: Normas para el manejo de la Historia Clínica*. https://www.minsalud.gov.co

Ministerio de Salud y Protección Social de Colombia. (2016). *Política de Atención Integral en Salud (PAIS)*. https://www.minsalud.gov.co

Newman, S. (2019). *Building microservices: Designing fine-grained systems* (2.ª ed.). O'Reilly Media.

Richardson, C. (2018). *Microservices patterns: With examples in Java*. Manning Publications.

U.S. Department of Health & Human Services. (2003). *Health Insurance Portability and Accountability Act (HIPAA)*. https://www.hhs.gov/hipaa
