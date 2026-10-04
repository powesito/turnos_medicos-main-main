# Sistema de Turnos Médicos (Django + Django REST Framework)

Aplicación web y **API REST** para gestionar especialidades, médicos, pacientes y turnos (citas) médicas.
Evaluación N.° 2 – Programación Backend.

## Funcionalidades

- **Especialidades y médicos**: cada médico tiene una especialidad, jornada laboral
  (hora de inicio/fin) y duración de turno configurable.
- **Pacientes**: registro simple con RUT/documento único.
- **Turnos**:
  - Agendar, ver detalle, cambiar estado (Pendiente, Confirmado, Cancelado, Atendido, No asistió) y cancelar.
  - Validaciones automáticas: no se permite agendar en el pasado, fuera del horario
    del médico, ni dos turnos en el mismo horario con el mismo médico (a nivel de
    base de datos con `UniqueConstraint` + validación en `clean()`).
  - Endpoint JSON (`/api/horarios-disponibles/`) que calcula los horarios libres
    de un médico en una fecha, usado por el formulario de agendamiento.
- **Panel de administración** de Django ya configurado (`/admin/`) para gestión
  interna rápida.
- Interfaz con Bootstrap 5, en español.

## Estructura del proyecto

```
turnos_medicos/
├── manage.py
├── requirements.txt
├── .env.example         # Plantilla de variables de entorno
├── docs/crear_base_datos.sql  # Script SQL: base de datos, usuario y permisos
├── config/              # Configuración del proyecto (settings, urls)
└── citas/                # App principal
    ├── models.py         # Especialidad, Medico, Paciente, Turno, HistorialTurno
    ├── admin.py
    ├── serializers.py    # ModelSerializer de cada modelo (API REST)
    ├── api_views.py      # ModelViewSet de cada modelo (API REST)
    ├── api_urls.py       # DefaultRouter con los endpoints (API REST)
    ├── forms.py
    ├── views.py          # Vistas con plantillas HTML (Evaluación 1)
    ├── urls.py
    ├── templates/citas/
    ├── static/citas/
    └── management/commands/cargar_datos_demo.py
```

## Instalación

1. Crea y activa el ambiente virtual (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate
   python -m pip install --upgrade pip
   ```
   Si Windows bloquea el script: `Set-ExecutionPolicy Bypass -Scope CurrentUser`.

2. Instala las librerías:
   ```
   pip install -r requirements.txt
   ```

3. Crea la base de datos y el usuario en MySQL ejecutando `docs/crear_base_datos.sql`
   como administrador (`mysql -u root -p`).

4. Crea el archivo `.env` copiando `.env.example` y revisa los valores: `SECRET_KEY` y las credenciales
   `DB_*` deben coincidir con las del paso 3. El `.env` no se sube al repositorio.

5. Crea las tablas (las migraciones ya vienen incluidas):
   ```
   python manage.py migrate
   ```

6. Crea el superusuario y carga datos de ejemplo:
   ```
   python manage.py createsuperuser
   python manage.py cargar_datos_demo
   ```

7. Inicia el servidor (con `DEBUG=False` agrega `--insecure` para que cargue el CSS):
   ```
   python manage.py runserver
   ```
   App: http://127.0.0.1:8000/ · Admin: http://127.0.0.1:8000/admin/ · API: http://127.0.0.1:8000/api/

Cada vez que cambies los modelos: `makemigrations` y `migrate`.
Cada vez que agregues una librería: `pip freeze > requirements.txt`.

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

Operaciones CRUD por recurso:

| Método | URL | Acción |
|---|---|---|
| GET | `/api/<recurso>/` | Listar (paginado de a 20) |
| GET | `/api/<recurso>/{id}/` | Detalle |
| POST | `/api/<recurso>/` | Crear |
| PUT | `/api/<recurso>/{id}/` | Reemplazar (todos los campos) |
| PATCH | `/api/<recurso>/{id}/` | Modificar parcialmente |
| DELETE | `/api/<recurso>/{id}/` | Eliminar |

Reglas de negocio en `/api/turnos/`: no se permiten fechas pasadas, horas fuera de la jornada del
médico ni dos turnos del mismo médico a la misma fecha y hora (el serializer reutiliza `Turno.clean()`).
Cada creación o cambio de estado queda registrado en el historial.

Ejemplo (crear un turno):

```
POST /api/turnos/
{"paciente": 1, "medico": 1, "fecha": "2026-10-20", "hora": "10:00:00", "motivo": "Control"}
```

Puedes probar todo desde el navegador (Browsable API de DRF), Postman o `curl`.

## Variables de entorno

Las credenciales no están en `settings.py`; se leen del archivo `.env` con `python-decouple`
(`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
El `.env` está en `.gitignore`; el repositorio incluye `.env.example` como plantilla.

## Flujo de uso típico

1. Entra a `/admin/` y crea (o usa el comando `cargar_datos_demo`) especialidades y médicos.
2. Registra un paciente desde "Nuevo paciente" en el menú.
3. Ve a "Agendar turno", elige paciente, médico, fecha y hora (el sistema te
   muestra los horarios libres del médico ese día).
4. Desde "Turnos" puedes filtrar por estado, médico o fecha, ver el detalle,
   cambiar su estado clínico o cancelarlo.

## Flujo URL → vista → plantilla

Django resuelve cada petición en tres pasos, y este proyecto los usa así:

1. **`config/urls.py`** (raíz del proyecto) incluye las rutas de la app con
   `include('citas.urls')`, y define `handler404` / `handler500` para los
   errores.
2. **`citas/urls.py`** mapea cada ruta a una vista concreta, por ejemplo
   `path('', views.HomeView.as_view(), name='home')` es la página de bienvenida.
3. La **vista** (en `citas/views.py`) procesa la lógica (consultas al ORM,
   validaciones, formularios) y llama a `render()` con una **plantilla** de
   `citas/templates/citas/`, que hereda de `base.html`.

### Página de bienvenida

La ruta raíz (`/`) apunta a `HomeView`, que muestra un resumen (médicos
activos, pacientes registrados, turnos de hoy) en vez de la página de
bienvenida por defecto de Django — confirma que la app está correctamente
conectada al proyecto.

### Página 404 personalizada

- `config/urls.py` define `handler404 = 'citas.views.error_404_view'`.
- `citas/views.py` → `error_404_view()` renderiza `citas/templates/citas/404.html`
  (hereda el diseño del sitio) devolviendo explícitamente `status=404`.
- También se agregó `handler500` con `citas/templates/citas/500.html` como
  buena práctica adicional.

**Cómo probarla:** Django solo usa `handler404`/`handler500` cuando
`DEBUG = False` (con `DEBUG = True` siempre verás la página de depuración de
Django con el traceback). Para probarla localmente:

```bash
# En config/settings.py, cambia temporalmente:
DEBUG = False

# Luego levanta el servidor y visita una URL que no existe, por ejemplo:
python manage.py runserver
# http://127.0.0.1:8000/esta-ruta-no-existe/
```

Verás la plantilla personalizada con el mensaje "😕 No encontramos la página
que buscas" en vez del error técnico de Django. No olvides volver a poner
`DEBUG = True` para seguir desarrollando.

## Próximos pasos sugeridos (no incluidos por simplicidad)

- Autenticación de pacientes/médicos con login propio y permisos por rol.
- Notificaciones por correo/SMS al confirmar o cancelar un turno.
- Recordatorios automáticos (Celery + cron).
- Autenticación en la API (token/JWT) y permisos por rol.

## Notas técnicas

- Base de datos: MySQL (configurada por variables de entorno `DB_*`). Para pruebas rápidas puedes usar
  SQLite con `DB_ENGINE=django.db.backends.sqlite3` y `DB_NAME=db.sqlite3` en el `.env`.
- Antes de desplegar en producción: `SECRET_KEY` nueva, `DEBUG=False` y `ALLOWED_HOSTS` correcto.
