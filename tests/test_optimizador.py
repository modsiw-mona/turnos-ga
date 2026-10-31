import numpy as np
import pytest

from turnos_ga.optimizador import resolver
from turnos_ga.problema import Problema


@pytest.fixture
def problema_pequeno():
    """
    4 personas, 2 días × 2 turnos, 2 por turno, máximo 2: la
    demanda (8) es igual a la capacidad (8), como en el caso base,
    pero el algoritmo lo resuelve en pocas generaciones.
    """

    return Problema(
        personas=("Ana", "Beto", "Carla", "Dani"),
        dias=2,
        turnos_por_dia=2,
        personas_por_turno=2,
        max_turnos_por_persona=2,
    )


def test_encuentra_horario_valido_en_el_caso_del_taller():

    # El resultado central del Taller U2: con la semilla 42 y los
    # mismos hiperparámetros, el algoritmo encuentra un horario sin
    # violaciones para 7 personas y 14 turnos.
    problema = Problema(
        personas=("Ana", "Beto", "Carla", "Dani", "Eva", "Fede", "Gabi")
    )

    resultado = resolver(problema, semilla=42)

    assert resultado.valido
    assert resultado.horario.shape == (14, 3)
    for turno in resultado.horario:
        assert len(set(turno)) == 3


def test_misma_semilla_produce_el_mismo_horario(problema_pequeno):

    primero = resolver(problema_pequeno, semilla=7)
    segundo = resolver(problema_pequeno, semilla=7)

    assert np.array_equal(primero.horario, segundo.horario)
    assert primero.generaciones == segundo.generaciones


def test_problema_imposible_falla_antes_de_buscar():

    problema = Problema(personas=("Ana", "Beto", "Carla"))

    with pytest.raises(ValueError):
        resolver(problema)
