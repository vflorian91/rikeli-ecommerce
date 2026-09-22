"""Verifica por HTTP los cuatro servicios y su acceso real a PostgreSQL y Redis."""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

suite = ET.Element("testsuite", name="Infraestructura Rikeli", tests="4")
failures = 0
for service in ("auth", "catalogo", "pedidos", "pagos"):
    case = ET.SubElement(suite, "testcase", name=f"{service}: HTTP, PostgreSQL y Redis", classname="infraestructura")
    try:
        with urllib.request.urlopen(f"http://{service}:8000/health", timeout=15) as response:
            data = json.load(response)
        assert data["service"] == service, "Servicio incorrecto"
        assert data["status"] == "ok", "Servicio no disponible"
        assert data["dependencies"] == {"postgres": "ok", "redis": "ok"}, "Dependencias no disponibles"
        print(f"PASS {service}")
    except Exception as error:
        failures += 1
        ET.SubElement(case, "failure", message=str(error))
        print(f"FAIL {service}: {error}")
suite.set("failures", str(failures))
Path("/results").mkdir(exist_ok=True)
ET.ElementTree(suite).write("/results/smoke.xml", encoding="utf-8", xml_declaration=True)
sys.exit(1 if failures else 0)
