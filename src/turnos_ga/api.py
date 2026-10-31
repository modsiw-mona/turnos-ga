from __future__ import annotations

import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, StringConstraints

from turnos_ga.optimizador import SEMILLA, resolver
from turnos_ga.problema import (
    Problema,
    describir_horario,
    turnos_por_persona,
    validar_problema,
)

# ============================================================
# Servicio de asignación de turnos — Unidad 4, Capítulo 4
#
# El servicio no guarda nada entre solicitudes: recibe el
# equipo y las reglas de la semana, corre el algoritmo
# genético y devuelve el horario (inferencia online).
#
# Secretos: la API key NO está en el código ni en la imagen.
# Se lee de la variable de entorno API_KEY (archivo .env en
# desarrollo, --env-file al ejecutar el contenedor). Si falta,
# el servicio no arranca: es preferible fallar al iniciar que
# quedar publicado en internet sin protección.
# ============================================================

PAGINA = Path(__file__).resolve().parent / "static" / "index.html"

_state: dict = {}


def cargar_configuracion() -> None:
    """Lee la API key del entorno."""

    api_key = os.environ.get("API_KEY", "")

    if not api_key:
        raise RuntimeError(
            "Falta la variable de entorno API_KEY. Copie .env.example "
            "a .env y defina una clave (ver README)."
        )

    _state["api_key"] = api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    cargar_configuracion()
    yield
    _state.clear()


app = FastAPI(
    title="Turnos GA — Servicio de asignación de turnos",
    description=(
        "Arma el horario semanal de un equipo con un algoritmo "
        "genético: cada turno con el número de personas pedido "
        "y nadie por encima del máximo de turnos."
    ),
    lifespan=lifespan,
)


# ============================================================
# Contrato de la API
# ============================================================

Nombre = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=40),
]


class SolicitudHorario(BaseModel):
    personas: list[Nombre] = Field(
        min_length=1,
        max_length=20,
        description="Nombres de las personas del equipo.",
    )
    dias: int = Field(default=7, ge=1, le=7, description="Días a cubrir.")
    turnos_por_dia: int = Field(
        default=2, ge=1, le=3, description="Jornadas por día (mañana, tarde, noche)."
    )
    personas_por_turno: int = Field(
        default=3, ge=1, description="Personas distintas que necesita cada turno."
    )
    max_turnos_por_persona: int = Field(
        default=6, ge=1, description="Máximo de turnos por persona en la semana."
    )
    semilla: int = Field(
        default=SEMILLA,
        description="Semilla del algoritmo (misma semilla, mismo horario).",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "personas": ["Ana", "Beto", "Carla", "Dani", "Eva", "Fede", "Gabi"],
                    "dias": 7,
                    "turnos_por_dia": 2,
                    "personas_por_turno": 3,
                    "max_turnos_por_persona": 6,
                }
            ]
        }
    }


class Turno(BaseModel):
    dia: str
    jornada: str
    personas: list[str]


class RespuestaHorario(BaseModel):
    valido: bool
    violaciones: dict[str, int]
    generaciones: int
    horario: list[Turno]
    turnos_por_persona: dict[str, int]


# ============================================================
# Utilidades
# ============================================================


def _verificar_api_key(clave: str | None) -> None:

    # compare_digest compara en tiempo constante: no revela,
    # por lo que tarda la comparación, cuántos caracteres
    # iniciales acertó quien intenta adivinar la clave.
    if clave is None or not secrets.compare_digest(clave, _state["api_key"]):
        raise HTTPException(
            status_code=401,
            detail="API key ausente o incorrecta (encabezado X-API-Key).",
        )


def _construir_problema(solicitud: SolicitudHorario) -> Problema:

    problema = Problema(
        personas=tuple(solicitud.personas),
        dias=solicitud.dias,
        turnos_por_dia=solicitud.turnos_por_dia,
        personas_por_turno=solicitud.personas_por_turno,
        max_turnos_por_persona=solicitud.max_turnos_por_persona,
    )

    try:
        validar_problema(problema)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return problema


# ============================================================
# Endpoints
# ============================================================


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def pagina() -> str:
    return PAGINA.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/horario", response_model=RespuestaHorario)
def horario(
    solicitud: SolicitudHorario,
    x_api_key: Annotated[str | None, Header()] = None,
) -> RespuestaHorario:

    _verificar_api_key(x_api_key)

    problema = _construir_problema(solicitud)

    resultado = resolver(problema, semilla=solicitud.semilla)

    return RespuestaHorario(
        valido=resultado.valido,
        violaciones=resultado.violaciones,
        generaciones=resultado.generaciones,
        horario=[Turno(**t) for t in describir_horario(problema, resultado.horario)],
        turnos_por_persona=turnos_por_persona(problema, resultado.horario),
    )
