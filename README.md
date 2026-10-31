# Turnos GA — asignación de turnos como servicio

Servicio que arma el horario semanal de un equipo con un algoritmo genético
(PyGAD). Parte del taller de la **Unidad 2** (`notebooks/Taller_U2_GA_Turnos.ipynb`)
y lo lleva a un servicio reproducible, verificable y publicable, como pide la
**Unidad 4** ("Despliegue de modelos de Inteligencia Artificial") del curso
*Técnicas avanzadas de IA*.

## La aplicación

**Quién la usa:** quien coordina los turnos de un equipo pequeño (un local,
un laboratorio, un turno de soporte) y necesita repartir la semana sin
hacerlo a mano.

**Qué hace:** recibe los nombres del equipo y las reglas de la semana, y
devuelve un horario donde:

1. **Cobertura:** cada turno tiene el número pedido de personas **distintas**.
2. **Máximo:** nadie trabaja más turnos de los permitidos en la semana.

Son las dos reglas del Taller U2. El caso por defecto es el del taller:
7 personas, 7 días × 2 turnos (mañana y tarde), 3 personas por turno y
máximo 6 turnos por persona. Si la semana es imposible (por ejemplo, el
equipo no alcanza para cubrir todos los cupos), el servicio responde de
inmediato con un error que explica por qué, sin correr el algoritmo.

**Cómo se usa:** desde una página web (`/`) o directamente por la API
(`POST /horario`), con una API key.

**Qué necesita:** solo Python y sus dependencias. No hay un modelo entrenado
que cargar ni servicios externos: en cada solicitud el algoritmo genético
busca el horario (inferencia online). Con la misma semilla, el mismo
horario.

## Estructura

```text
turnos-ga/
├── .python-version        → ¿qué Python utilizamos? (3.12)
├── pyproject.toml         → ¿qué necesita el proyecto?
├── uv.lock                → ¿qué versiones concretas utilizamos?
├── .env.example           → ¿qué secretos hay que configurar?
├── Dockerfile             → ¿cómo se construye la imagen del servicio?
├── .dockerignore          → ¿qué no entra a la imagen?
├── .github/workflows/     → integración continua
├── notebooks/             → exploración original de la Unidad 2
├── src/turnos_ga/
│   ├── problema.py        → reglas, fitness y validación del problema
│   ├── optimizador.py     → algoritmo genético (PyGAD) y uso por terminal
│   ├── api.py             → servicio FastAPI
│   └── static/index.html  → página web
└── tests/                 → pruebas automatizadas
```

`pyproject.toml` separa las dependencias del **servicio** (`fastapi`,
`uvicorn`, `numpy`, `pygad`) de las de **desarrollo** (grupo `dev`:
`pytest`, `ruff`, `httpx2`). `uv sync` instala ambas; la imagen de Docker
solo las primeras.

## Cómo navegar el historial

Cada etapa del proyecto quedó marcada con un tag de Git:

```bash
git tag -l -n1
```

| Tag | Qué muestra |
|---|---|
| `etapa0-esqueleto` | `pyproject.toml`, `uv.lock`, `.python-version` y el notebook de la U2. |
| `etapa1-modulos` | La lógica del notebook organizada en módulos y ejecutable como script. |
| `etapa2-servicio` | Servicio FastAPI con `/health`, `POST /horario` y la API key leída del entorno. |
| `etapa3-pruebas` | Pruebas automatizadas con pytest. |
| `etapa4-calidad-codigo` | El código cumple Ruff (linting y formato). |
| `etapa5-contenedor` | Dockerfile mínimo con health check y `.dockerignore`. |
| `etapa6-integracion-continua` | GitHub Actions: Ruff, pytest, build de la imagen y `/health`. |

## Instalación

Requiere [uv](https://docs.astral.sh/uv/getting-started/installation/) y Git.
No hace falta instalar Python: uv descarga la versión fijada en
`.python-version`.

```bash
git clone https://github.com/modsiw-mona/turnos-ga.git
cd turnos-ga
uv sync
```

`uv sync` reconstruye el ambiente en `.venv/` con exactamente las versiones
de `uv.lock`.

## Configurar el secreto

`POST /horario` exige una API key en el encabezado `X-API-Key`. La clave se
lee de la variable de entorno `API_KEY` y **nunca** se escribe en el código
ni entra a la imagen.

```bash
cp .env.example .env
# Generar una clave aleatoria y pegarla en .env, en API_KEY=...
uv run python -c "import secrets; print(secrets.token_urlsafe(16))"
```

- `.env` está en `.gitignore` (no se versiona) y en `.dockerignore` (no entra
  a la imagen).
- `.env.example` sí se versiona: documenta qué variables definir, sin valores
  reales.
- Si `API_KEY` no está definida, el servicio **no arranca**: es preferible
  fallar al iniciar que quedar publicado en internet sin protección.

## Ejecutar el servicio

```bash
uv run --env-file .env uvicorn turnos_ga.api:app --reload
```

| Ruta | Qué hace |
|---|---|
| `GET /` | Página web para armar el horario. |
| `GET /docs` | Documentación interactiva de la API (FastAPI). |
| `GET /health` | Confirma que el servicio está arriba: `{"status": "ok"}`. |
| `POST /horario` | Recibe el equipo y las reglas, devuelve el horario. |

Ejemplo de solicitud a `POST /horario` (con el encabezado `X-API-Key`):

```json
{
  "personas": ["Ana", "Beto", "Carla", "Dani", "Eva", "Fede", "Gabi"],
  "dias": 7,
  "turnos_por_dia": 2,
  "personas_por_turno": 3,
  "max_turnos_por_persona": 6
}
```

La respuesta indica si el horario es válido, sus violaciones (0 si lo es),
cuántas generaciones tardó el algoritmo, el horario turno por turno y
cuántos turnos le tocan a cada persona.

| Código | Cuándo |
|---|---|
| `200` | Horario generado. |
| `401` | Falta la API key o es incorrecta. |
| `422` | La entrada no cumple el contrato (tipos, rangos) o la semana es imposible. |

Sin levantar el servicio, desde la terminal:

```bash
uv run python -m turnos_ga.optimizador --personas Ana Beto Carla Dani Eva Fede Gabi
```

## Pruebas y calidad de código

```bash
uv run pytest -v                # 18 pruebas
uv run ruff check .             # linting
uv run ruff format --check .    # formato
```

Las pruebas verifican la lógica principal, sin necesitar el servicio
corriendo:

- **`test_problema.py`**: `evaluar` da 0 violaciones en un horario válido
  construido a mano y detecta personas repetidas en un turno y personas por
  encima del máximo; `validar_problema` rechaza semanas imposibles, turnos
  con más personas que el equipo y nombres repetidos.
- **`test_optimizador.py`**: el algoritmo encuentra un horario válido en el
  caso del Taller U2 (semilla 42), la misma semilla produce el mismo horario
  y un problema imposible falla antes de buscar.
- **`test_api.py`**: con `TestClient` de FastAPI, `/health` responde, `POST
  /horario` responde 401 sin API key o con una incorrecta, 200 con un horario
  que respeta las reglas, 422 ante una semana imposible, y el servicio no
  arranca sin `API_KEY`.

## Contenedor

Requiere Docker Desktop en ejecución.

```bash
docker build -t turnos-ga-api .
docker run --rm -p 8000:8000 --env-file .env turnos-ga-api
```

Qué entra y qué no entra a la imagen:

| Entra | No entra |
|---|---|
| Python 3.12 (`python:3.12-slim`) | `notebooks/` |
| `fastapi`, `uvicorn`, `numpy`, `pygad` (`uv sync --no-default-groups --frozen`) | `tests/` y herramientas de desarrollo (`pytest`, `ruff`, `httpx2`) |
| `src/turnos_ga/` (código y página) | `.env` (la clave se entrega al ejecutar con `--env-file`) |

El `Dockerfile` define un `HEALTHCHECK` que consulta `/health` cada 30
segundos; `docker ps` muestra el contenedor como `healthy`.

## Publicación con un túnel temporal de Cloudflare

Con el contenedor en ejecución, en otra terminal:

```bash
# instalar una sola vez (macOS): brew install cloudflared
cloudflared tunnel --url http://localhost:8000
```

Aparece una dirección `https://<palabras-al-azar>.trycloudflare.com`. Desde
cualquier dispositivo (por ejemplo, un celular con datos móviles) se abre esa
dirección, se escribe la API key en la página y se genera el horario.

El túnel es para demostraciones, no para producción: la dirección cambia cada
vez, deja de existir al cerrar `cloudflared` (Ctrl+C) y solo funciona
mientras el computador y el contenedor sigan encendidos.

## Integración continua

`.github/workflows/ci.yml` se ejecuta en cada push, en una máquina limpia de
GitHub:

1. **Calidad y pruebas:** instala el proyecto desde `uv.lock`
   (`uv sync --locked`) y ejecuta Ruff y pytest.
2. **Imagen de Docker:** si lo anterior pasó, construye la imagen, inicia el
   servicio con una API key desechable y verifica que `/health` responda.
