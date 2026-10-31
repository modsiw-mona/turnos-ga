# Servicio de asignación de turnos — Unidad 4.
#
# Imagen de una sola etapa, deliberadamente mínima: solo entra lo que
# el servicio necesita para responder /, /health y /horario.
#
# Lo que NO entra a esta imagen (ver .dockerignore):
#   - el notebook de exploración (notebooks/)
#   - las pruebas (tests/) y las dependencias de desarrollo (pytest, ruff)
#   - el archivo .env con la API key: el secreto se entrega al
#     ejecutar el contenedor (--env-file .env), nunca al construirlo

FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# --no-default-groups excluye el grupo "dev": la imagen solo instala
# lo declarado en [project.dependencies] -fastapi, uvicorn, numpy,
# pygad-. Se copian primero pyproject.toml y uv.lock para que Docker
# reutilice esta capa mientras las dependencias no cambien.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-default-groups --frozen --no-install-project

# Solo el paquete del servicio (código + página web).
COPY src/turnos_ga/ src/turnos_ga/

ENV PYTHONPATH=/app/src

EXPOSE 8000

# Docker consulta /health cada 30 s y marca el contenedor como
# "healthy" o "unhealthy" (visible en docker ps). La imagen no trae
# curl, así que se usa la librería estándar de Python.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=4)"]

# No usar "uv run" aquí: resincronizaría el entorno con el grupo dev en
# cada arranque. Se invoca uvicorn directamente desde el venv del build.
CMD ["/app/.venv/bin/uvicorn", "turnos_ga.api:app", "--host", "0.0.0.0", "--port", "8000"]
