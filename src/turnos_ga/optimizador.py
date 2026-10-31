from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pygad

from turnos_ga.problema import (
    Problema,
    decodificar,
    describir_horario,
    evaluar,
    turnos_por_persona,
    validar_problema,
)

# ============================================================
# Algoritmo genético (PyGAD)
#
# Hiperparámetros del Taller U2: la configuración que encontró
# un horario válido en las 5 semillas probadas (mutación 5 %).
# Son configuración, no lógica: viven aquí, en un solo lugar,
# en vez de repetirse dentro del código.
# ============================================================

GENERACIONES = 300
TAMANO_POBLACION = 100
PADRES = 33
K_TORNEO = 3
MUTACION_PORCENTAJE = 5
ELITISMO = 2
SEMILLA = 42


@dataclass
class Resultado:
    horario: np.ndarray
    violaciones: dict[str, int]
    generaciones: int

    @property
    def valido(self) -> bool:
        return self.violaciones["violaciones"] == 0


def resolver(problema: Problema, semilla: int = SEMILLA) -> Resultado:
    """
    Busca un horario sin violaciones.

    Se detiene al llegar a fitness 0 (horario válido) o al
    agotar las generaciones. En ese caso devuelve el mejor
    horario encontrado, con sus violaciones: quien lo use debe
    revisar Resultado.valido.
    """

    validar_problema(problema)

    def fitness_func(ga_instance, solution, solution_idx):
        return -evaluar(problema, decodificar(problema, solution))["violaciones"]

    ga = pygad.GA(
        num_generations=GENERACIONES,
        sol_per_pop=TAMANO_POBLACION,
        num_parents_mating=PADRES,
        num_genes=problema.num_genes,
        fitness_func=fitness_func,
        gene_type=int,
        gene_space=list(range(problema.num_personas)),
        parent_selection_type="tournament",
        K_tournament=K_TORNEO,
        crossover_type="single_point",
        mutation_type="random",
        mutation_percent_genes=MUTACION_PORCENTAJE,
        keep_elitism=ELITISMO,
        stop_criteria="reach_0",
        random_seed=semilla,
        suppress_warnings=True,
    )

    ga.run()

    mejor, _, _ = ga.best_solution(pop_fitness=ga.last_generation_fitness)
    horario = decodificar(problema, mejor)

    return Resultado(
        horario=horario,
        violaciones=evaluar(problema, horario),
        generaciones=ga.generations_completed,
    )


# ============================================================
# Uso desde la terminal
# ============================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Asigna los turnos de una semana con un algoritmo genético."
    )
    parser.add_argument(
        "--personas",
        nargs="+",
        default=[f"Persona {i}" for i in range(1, 8)],
    )
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    args = parser.parse_args()

    problema = Problema(personas=tuple(args.personas))
    resultado = resolver(problema, semilla=args.semilla)

    for turno in describir_horario(problema, resultado.horario):
        print(f"{turno['dia']:9s} {turno['jornada']:6s} | {', '.join(turno['personas'])}")

    print()
    print("Turnos por persona:", turnos_por_persona(problema, resultado.horario))
    print("Violaciones:", resultado.violaciones)
    print("Generaciones:", resultado.generaciones)


if __name__ == "__main__":
    main()
