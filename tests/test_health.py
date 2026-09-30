"""Pruebas de integración de los microservicios de Rikeli."""

import json
import urllib.request

import pytest


SERVICIOS = ("auth", "catalogo", "pedidos", "pagos")


@pytest.mark.parametrize("servicio", SERVICIOS)
def test_health_servicio(servicio):
    """Comprueba HTTP, PostgreSQL y Redis para cada microservicio."""

    url = f"http://{servicio}:8000/health"

    with urllib.request.urlopen(url, timeout=15) as respuesta:
        datos = json.load(respuesta)

    assert respuesta.status == 200
    assert datos["service"] == servicio
    assert datos["status"] == "ok"
    assert datos["dependencies"]["postgres"] == "ok"
    assert datos["dependencies"]["redis"] == "ok"