import numpy as np
import pytest

from turnos_ga.problema import (
    Problema,
    describir_horario,
    evaluar,
    turnos_por_persona,
    validar_problema,
)

EQUIPO = ("Ana", "Beto", "Carla", "Dani", "Eva", "Fede", "Gabi")


@pytest.fixture
def problema_base():
    """El caso del Taller U2: 7 personas, 14 turnos, 3 por turno, máximo 6."""

    return Problema(personas=EQUIPO)


@pytest.fixture
def horario_valido():
    """
    Horario válido construido a mano: el turno t lo cubren las
    personas t, t+1 y t+2 (módulo 7). En 14 turnos cada persona
    aparece exactamente 6 veces y nunca se repite en un turno.
    """

    return np.array([[t % 7, (t + 1) % 7, (t + 2) % 7] for t in range(14)])


class TestEvaluar:
    def test_horario_valido_no_tiene_violaciones(self, problema_base, horario_valido):

        assert evaluar(problema_base, horario_valido) == {
            "violaciones": 0,
            "repeticiones": 0,
            "excesos": 0,
        }

    def test_detecta_persona_repetida_en_un_turno(self, problema_base, horario_valido):

        horario = horario_valido.copy()
        horario[0] = [0, 0, 1]  # Ana ocupa dos cupos del mismo turno

        resultado = evaluar(problema_base, horario)

        assert resultado["repeticiones"] == 1

    def test_detecta_persona_por_encima_del_maximo(self, problema_base, horario_valido):

        horario = horario_valido.copy()
        horario[:, 0] = 0  # Ana en los 14 turnos: 8 por encima del máximo

        resultado = evaluar(problema_base, horario)

        assert resultado["excesos"] >= 8
        assert resultado["violaciones"] > 0


class TestValidarProblema:
    def test_acepta_el_caso_base(self, problema_base):
        validar_problema(problema_base)

    def test_rechaza_demanda_mayor_que_capacidad(self):

        # 14 turnos × 3 = 42 cupos, pero 3 personas × 6 = 18
        problema = Problema(personas=("Ana", "Beto", "Carla"))

        with pytest.raises(ValueError, match="42 asignaciones"):
            validar_problema(problema)

    def test_rechaza_turnos_con_mas_personas_que_el_equipo(self):

        problema = Problema(
            personas=("Ana", "Beto"),
            dias=1,
            turnos_por_dia=1,
            personas_por_turno=3,
        )

        with pytest.raises(ValueError, match="personas distintas"):
            validar_problema(problema)

    def test_rechaza_nombres_repetidos(self):

        problema = Problema(personas=("Ana", "Ana", "Beto", "Carla"))

        with pytest.raises(ValueError, match="repetidos"):
            validar_problema(problema)


class TestDescribirHorario:
    def test_traduce_indices_a_dias_jornadas_y_nombres(
        self, problema_base, horario_valido
    ):

        turnos = describir_horario(problema_base, horario_valido)

        assert len(turnos) == 14
        assert turnos[0] == {
            "dia": "Lunes",
            "jornada": "mañana",
            "personas": ["Ana", "Beto", "Carla"],
        }
        assert turnos[13]["dia"] == "Domingo"
        assert turnos[13]["jornada"] == "tarde"

    def test_cuenta_turnos_por_persona(self, problema_base, horario_valido):

        conteo = turnos_por_persona(problema_base, horario_valido)

        assert conteo == {nombre: 6 for nombre in EQUIPO}
