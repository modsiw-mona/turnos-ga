# Turnos GA — asignación de turnos como servicio

Servicio que arma el horario semanal de un equipo con un algoritmo genético
(PyGAD). Parte del taller de la **Unidad 2** (`notebooks/Taller_U2_GA_Turnos.ipynb`)
y lo lleva a un servicio reproducible, verificable y publicable, como pide la
**Unidad 4** ("Despliegue de modelos de Inteligencia Artificial") del curso
*Técnicas avanzadas de IA*.

> Proyecto en construcción. Este README se completa a medida que avanza el
> historial (ver los tags de Git).

## Estructura

```text
turnos-ga/
├── .python-version      → ¿qué Python utilizamos?
├── pyproject.toml       → ¿qué necesita el proyecto?
├── uv.lock              → ¿qué versiones concretas utilizamos?
├── notebooks/           → exploración original de la Unidad 2
├── src/turnos_ga/       → lógica reutilizable
└── tests/               → pruebas automatizadas
```

## Instalación

```bash
git clone <url-del-repositorio>
cd turnos-ga
uv sync
```

## Configurar el secreto

El servicio exige una API key en el encabezado `X-API-Key`. La clave se lee
de la variable de entorno `API_KEY` y **nunca** se escribe en el código:

```bash
cp .env.example .env
# edite .env y reemplace el valor de API_KEY
```

`.env` está en `.gitignore`. Si `API_KEY` no está definida, el servicio no
arranca.

## Ejecutar el servicio

```bash
uv run --env-file .env uvicorn turnos_ga.api:app --reload
```

- `http://localhost:8000/` — página para armar el horario.
- `http://localhost:8000/docs` — documentación interactiva de la API.
- `GET /health` — confirma que el servicio está arriba.
- `POST /horario` — recibe el equipo y las reglas, devuelve el horario.

Desde la terminal, sin servicio:

```bash
uv run python -m turnos_ga.optimizador --personas Ana Beto Carla Dani Eva Fede Gabi
```
