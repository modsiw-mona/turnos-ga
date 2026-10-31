import pytest
from fastapi.testclient import TestClient

from turnos_ga import api

CLAVE = "clave-de-prueba"

# Problema pequeño para que las pruebas del servicio sean rápidas.
SOLICITUD = {
    "personas": ["Ana", "Beto", "Carla", "Dani"],
    "dias": 2,
    "turnos_por_dia": 2,
    "personas_por_turno": 2,
    "max_turnos_por_persona": 2,
}


@pytest.fixture
def cliente(monkeypatch):
    """
    Levanta el servicio en memoria con una API key de prueba.
    TestClient ejecuta el lifespan, así que la clave se lee del
    entorno igual que en producción.
    """

    monkeypatch.setenv("API_KEY", CLAVE)

    with TestClient(api.app) as cliente:
        yield cliente


def test_health_responde_ok(cliente):

    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_horario_sin_api_key_es_rechazado(cliente):

    respuesta = cliente.post("/horario", json=SOLICITUD)

    assert respuesta.status_code == 401


def test_horario_con_api_key_incorrecta_es_rechazado(cliente):

    respuesta = cliente.post(
        "/horario", json=SOLICITUD, headers={"X-API-Key": "otra-clave"}
    )

    assert respuesta.status_code == 401


def test_horario_valido_respeta_las_reglas(cliente):

    respuesta = cliente.post("/horario", json=SOLICITUD, headers={"X-API-Key": CLAVE})

    assert respuesta.status_code == 200

    datos = respuesta.json()
    assert datos["valido"] is True
    assert len(datos["horario"]) == 4
    assert all(len(turno["personas"]) == 2 for turno in datos["horario"])
    assert max(datos["turnos_por_persona"].values()) <= 2


def test_problema_imposible_responde_422(cliente):

    solicitud = {**SOLICITUD, "personas": ["Ana", "Beto"]}

    respuesta = cliente.post("/horario", json=solicitud, headers={"X-API-Key": CLAVE})

    assert respuesta.status_code == 422
    assert "asignaciones" in respuesta.json()["detail"]


def test_servicio_no_arranca_sin_api_key(monkeypatch):

    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="API_KEY"):
        with TestClient(api.app):
            pass
