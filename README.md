# Sistema de Turnos Médicos (Django + Django REST Framework)

API REST y aplicación web para gestionar especialidades, médicos, pacientes y turnos (citas) médicas.

**Asignatura:** Programación Backend · **Evaluación N.° 2** – Desarrollo de API REST con Django REST Framework

## Funcionalidades

- **Especialidades y médicos**: cada médico tiene una especialidad, jornada laboral
  (hora de inicio/fin) y duración de turno configurable.
- **Pacientes**: registro simple con RUT/documento único.
- **Turnos**:
  - Agendar, ver detalle, cambiar estado (Pendiente, Confirmado, Cancelado, Atendido, No asistió) y cancelar.
  - Validaciones automáticas: no se permite agendar en el pasado, fuera del horario
    del médico, ni dos turnos activos en el mismo horario con el mismo médico
    (validación en `Turno.clean()`, reutilizada por el serializer de la API).
  - Historial de cambios de estado (`HistorialTurno`) registrado automáticamente desde la API.
- **API REST completa** (CRUD) para los 5 modelos, con Django REST Framework.
- **Panel de administración** de Django configurado (`/admin/`).
- Interfaz web con Bootstrap 5, en español (Evaluación N.° 1).

## Tecnologías

- Python 3 · Django 6.1 · Django REST Framework 3.18
- MySQL (con `mysqlclient`)
- `python-decouple` para variables de entorno

## Estructura del proyecto

```
turnos_medicos/
├── manage.py
├── requirements.txt
├── .env                       # Variables de entorno (SECRET_KEY, DB_*)
├── docs/crear_base_datos.sql  # Script SQL: base de datos, usuario y permisos
├── config/                    # Configuración del proyecto (settings, urls)
└── citas/                     # App principal
    ├── models.py              # Especialidad, Medico, Paciente, Turno, HistorialTurno
    ├── migrations/            # 0001_initial, 0002, 0003_historialturno
    ├── admin.py
    ├── serializers.py         # ModelSerializer de cada modelo (API REST)
    ├── api_views.py           # ModelViewSet de cada modelo (API REST)
    ├── api_urls.py            # DefaultRouter con los endpoints (API REST)
    ├── forms.py
    ├── views.py               # Vistas con plantillas HTML (Evaluación 1)
    ├── urls.py
    ├── templates/citas/
    ├── static/citas/
    └── management/commands/cargar_datos_demo.py
```

## Modelo de datos

| Modelo | Campos principales | Relaciones |
|---|---|---|
| `Especialidad` | nombre (único), descripcion | 1 especialidad → N médicos |
| `Medico` | nombre_completo, email, telefono, duracion_turno_min, hora_inicio_jornada, hora_fin_jornada, activo | FK a `Especialidad` (PROTECT); OneToOne opcional a `User` |
| `Paciente` | nombre_completo, rut_o_documento (único), email, telefono, fecha_nacimiento | OneToOne opcional a `User` |
| `Turno` | fecha, hora, motivo, estado, notas, creado_en, actualizado_en | FK a `Paciente` y a `Medico` (CASCADE) |
| `HistorialTurno` | estado_anterior, estado_nuevo, descripcion, creado_en | FK a `Turno` (CASCADE); FK opcional a `User` |

## Instalación

1. Crea y activa el ambiente virtual (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate
   python -m pip install --upgrade pip
   ```
   En Linux/macOS: `source .venv/bin/activate`.
   Si Windows bloquea el script: `Set-ExecutionPolicy Bypass -Scope CurrentUser`.

2. Instala las librerías:
   ```
   pip install -r requirements.txt
   ```

3. Crea la base de datos, el usuario y sus permisos en MySQL ejecutando `docs/crear_base_datos.sql`
   como administrador:
   ```
   mysql -u root -p < docs/crear_base_datos.sql
   ```

4. El archivo `.env` ya viene incluido en el repositorio. Revisa que `SECRET_KEY` y las
   credenciales `DB_*` coincidan con las del paso 3.

5. Aplica las migraciones (ya vienen incluidas en el repositorio):
   ```
   python manage.py migrate
   ```

6. Crea el superusuario y carga datos de ejemplo:
   ```
   python manage.py createsuperuser
   python manage.py cargar_datos_demo
   ```

7. Inicia el servidor:
   ```
   python manage.py runserver
   ```
   - Aplicación: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - API: http://127.0.0.1:8000/api/

   > Si `DEBUG=False`, agrega `--insecure` (`python manage.py runserver --insecure`)
   > para que se carguen los estilos CSS del admin y de la Browsable API.

Cada vez que cambies los modelos: `python manage.py makemigrations` y `python manage.py migrate`.
Cada vez que agregues una librería: `pip freeze > requirements.txt`.

## Configuración de base de datos (scripts SQL)

El script `docs/crear_base_datos.sql` realiza:

- **Crear la base de datos** `turnos_medicos` (utf8mb4).
- **Crear el usuario** `turnos_user` con contraseña.
- **Asignar permisos**: `GRANT ALL PRIVILEGES` solo sobre `turnos_medicos.*`.
- `FLUSH PRIVILEGES` para aplicar los cambios.

## Variables de entorno

Las credenciales **no están escritas en `settings.py`**: se leen desde el archivo `.env`
con `python-decouple`.

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | Modo depuración (`True` en desarrollo) |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma |
| `DB_ENGINE` | Motor de base de datos (`django.db.backends.mysql`) |
| `DB_NAME` | Nombre de la base de datos |
| `DB_USER` | Usuario de la aplicación |
| `DB_PASSWORD` | Contraseña del usuario |
| `DB_HOST` | Host de la base de datos |
| `DB_PORT` | Puerto (3306) |

El archivo `.env` se incluye en el repositorio por requerimiento de la evaluación
(para que el proyecto pueda ejecutarse y revisarse). **En un proyecto real el `.env` debe
ir en `.gitignore`** y solo se versionaría una plantilla sin credenciales.

## API REST

Implementada con Django REST Framework: un `ModelSerializer` y un `ModelViewSet` por modelo,
registrados con `DefaultRouter` en `citas/api_urls.py` e incluidos en `config/urls.py` bajo `/api/`.

| Recurso | Endpoint (lista) | Endpoint (detalle) |
|---|---|---|
| Especialidades | `/api/especialidades/` | `/api/especialidades/{id}/` |
| Médicos | `/api/medicos/` | `/api/medicos/{id}/` |
| Pacientes | `/api/pacientes/` | `/api/pacientes/{id}/` |
| Turnos | `/api/turnos/` | `/api/turnos/{id}/` |
| Historial de turnos | `/api/historial/` | `/api/historial/{id}/` |

Operaciones CRUD disponibles en cada recurso:

| Método | URL | Acción |
|---|---|---|
| GET | `/api/<recurso>/` | Listar (paginado de a 20) |
| GET | `/api/<recurso>/{id}/` | Detalle |
| POST | `/api/<recurso>/` | Crear |
| PUT | `/api/<recurso>/{id}/` | Reemplazar (todos los campos) |
| PATCH | `/api/<recurso>/{id}/` | Modificar parcialmente |
| DELETE | `/api/<recurso>/{id}/` | Eliminar |

### Reglas de negocio en `/api/turnos/`

- No se permiten fechas pasadas.
- No se permiten horas fuera de la jornada del médico.
- No se permiten dos turnos activos del mismo médico a la misma fecha y hora.
- Cada creación o cambio de estado queda registrado en `HistorialTurno`.

(El serializer reutiliza `Turno.clean()`, y `TurnoViewSet` sobrescribe `perform_create` y
`perform_update` para generar el historial.)

### Ejemplos

Crear un turno:

```
POST /api/turnos/
Content-Type: application/json

{"paciente": 1, "medico": 1, "fecha": "2026-10-20", "hora": "10:00:00", "motivo": "Control"}
```

Modificar solo el estado:

```
PATCH /api/turnos/1/
Content-Type: application/json

{"estado": "CONFIRMADO"}
```

Eliminar:

```
DELETE /api/turnos/1/
```

Con `curl`:

```
curl http://127.0.0.1:8000/api/medicos/
curl -X POST http://127.0.0.1:8000/api/especialidades/ \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Neurología", "descripcion": "Sistema nervioso"}'
```

También puedes probar todo desde el navegador (Browsable API de DRF) o con Postman.

## Evidencias de la evaluación

- **Modelo de datos:** `citas/models.py`
- **Migraciones:** `citas/migrations/`
- **Scripts SQL:** `docs/crear_base_datos.sql`
- **Variables de entorno:** `.env`
- **Repositorio GitHub:** con historial de commits (URL entregada en la plataforma)

## Flujo URL → vista → plantilla (Evaluación 1)

1. **`config/urls.py`** incluye las rutas de la API (`api/`) y de la app web con `include(...)`,
   y define `handler404` / `handler500`.
2. **`citas/urls.py`** mapea cada ruta de la interfaz web a una vista;
   **`citas/api_urls.py`** registra los ViewSets de la API en el router.
3. Las vistas web (`citas/views.py`) procesan la lógica y renderizan plantillas de
   `citas/templates/citas/`, que heredan de `base.html`.

### Páginas de error personalizadas

`handler404` y `handler500` renderizan `citas/templates/citas/404.html` y `500.html`.
Django solo los usa cuando `DEBUG=False`. Para probarlo, pon `DEBUG=False` en el `.env`,
levanta el servidor con `runserver --insecure` y visita una URL inexistente.

## Próximos pasos sugeridos

- Autenticación en la API (token/JWT) y permisos por rol.
- Notificaciones por correo/SMS al confirmar o cancelar un turno.
- Recordatorios automáticos (Celery + cron).

## Notas técnicas

- Base de datos: MySQL (configurada por variables `DB_*`). Para pruebas rápidas se puede usar
  SQLite con `DB_ENGINE=django.db.backends.sqlite3` y `DB_NAME=db.sqlite3` en el `.env`.
- Antes de desplegar en producción: `SECRET_KEY` nueva, `DEBUG=False` y `ALLOWED_HOSTS` correcto.
