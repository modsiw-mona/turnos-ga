from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ============================================================
# El problema de asignación de turnos (Unidad 2)
#
# Un equipo de P personas cubre T turnos en la semana
# (T = días × turnos por día) con dos reglas:
#
#   1. Cobertura: cada turno necesita K personas distintas.
#   2. Máximo: nadie trabaja más de M turnos en la semana.
#
# Un horario se representa como un cromosoma de T·K enteros
# entre 0 y P-1: un gen por cupo, cuyo valor es la persona
# asignada. Las reglas no las garantiza la representación:
# las controla el fitness (evaluar).
# ============================================================

DIAS_SEMANA = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

JORNADAS = ["mañana", "tarde", "noche"]


@dataclass(frozen=True)
class Problema:
    """Datos de una semana: quiénes trabajan y qué hay que cubrir."""

    personas: tuple[str, ...]
    dias: int = 7
    turnos_por_dia: int = 2
    personas_por_turno: int = 3
    max_turnos_por_persona: int = 6

    @property
    def num_personas(self) -> int:
        return len(self.personas)

    @property
    def num_turnos(self) -> int:
        return self.dias * self.turnos_por_dia

    @property
    def num_genes(self) -> int:
        return self.num_turnos * self.personas_por_turno


def validar_problema(problema: Problema) -> None:
    """
    Falla pronto si el problema no tiene solución posible.

    Antes de correr el algoritmo genético (que puede tardar
    segundos) comprobamos las condiciones que hacen imposible
    cualquier horario válido. Así el error es inmediato y
    explica qué cambiar, en lugar de devolver un horario con
    violaciones.
    """

    if len(set(problema.personas)) != problema.num_personas:
        raise ValueError("Hay nombres de personas repetidos.")

    if problema.personas_por_turno > problema.num_personas:
        raise ValueError(
            f"Cada turno necesita {problema.personas_por_turno} personas "
            f"distintas, pero el equipo solo tiene {problema.num_personas}."
        )

    demanda = problema.num_turnos * problema.personas_por_turno
    capacidad = problema.num_personas * problema.max_turnos_por_persona

    if demanda > capacidad:
        raise ValueError(
            f"La semana necesita {demanda} asignaciones, pero el equipo "
            f"solo puede cubrir {capacidad} "
            f"({problema.num_personas} personas × "
            f"{problema.max_turnos_por_persona} turnos)."
        )


def decodificar(problema: Problema, cromosoma: np.ndarray) -> np.ndarray:
    """Convierte el cromosoma (T·K genes) en la matriz turnos × cupos."""

    return np.asarray(cromosoma, dtype=int).reshape(
        problema.num_turnos, problema.personas_por_turno
    )


def evaluar(problema: Problema, horario: np.ndarray) -> dict[str, int]:
    """
    Cuenta las violaciones de cada regla.

    - repeticiones: en cada turno, K - personas distintas.
    - excesos: para cada persona, max(0, turnos asignados - M).

    Un horario válido tiene cero violaciones.
    """

    horario = np.asarray(horario, dtype=int)

    # Cobertura: personas repetidas dentro de un turno
    repeticiones = 0
    for turno in range(problema.num_turnos):
        repeticiones += problema.personas_por_turno - len(np.unique(horario[turno]))

    # Máximo: turnos por encima de M
    excesos = 0
    for persona in range(problema.num_personas):
        turnos = np.count_nonzero(np.any(horario == persona, axis=1))
        excesos += max(0, turnos - problema.max_turnos_por_persona)

    return {
        "violaciones": int(repeticiones + excesos),
        "repeticiones": int(repeticiones),
        "excesos": int(excesos),
    }


def describir_horario(problema: Problema, horario: np.ndarray) -> list[dict]:
    """Traduce la matriz de enteros a días, jornadas y nombres."""

    turnos = []

    for turno in range(problema.num_turnos):
        dia, jornada = divmod(turno, problema.turnos_por_dia)

        nombres = sorted({problema.personas[p] for p in horario[turno]})

        turnos.append(
            {
                "dia": DIAS_SEMANA[dia],
                "jornada": JORNADAS[jornada],
                "personas": nombres,
            }
        )

    return turnos


def turnos_por_persona(problema: Problema, horario: np.ndarray) -> dict[str, int]:
    """Cuántos turnos distintos trabaja cada persona."""

    return {
        nombre: int(np.count_nonzero(np.any(horario == persona, axis=1)))
        for persona, nombre in enumerate(problema.personas)
    }
