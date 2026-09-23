# Rikeli Comercio electronico y lealtad

Prototipo academico del Grupo 1 para el Seminario de Graduacion.

## Estado actual

Base de infraestructura: cuatro servicios Python/FastAPI, PostgreSQL y Redis.
Esta version permite verificar conexiones; las funciones comerciales estan pendientes.

## Requisitos

Docker Desktop iniciado, Git y acceso al repositorio. Python se ejecuta en contenedores.

## Inicio local

El archivo `.env` local contiene la configuracion privada y no se sube a Git.
En otra computadora, copiar `.env.example` a `.env` y cambiar la clave de PostgreSQL.

```powershell
docker compose up -d --build --wait
```

| Servicio | Documentacion | Comprobacion |
|---|---|---|
| Autenticacion | http://localhost:8001/docs | http://localhost:8001/health |
| Catalogo | http://localhost:8002/docs | http://localhost:8002/health |
| Pedidos | http://localhost:8003/docs | http://localhost:8003/health |
| Pagos | http://localhost:8004/docs | http://localhost:8004/health |

## Pruebas

Con los servicios encendidos:

```powershell
docker compose run --rm tests
```

Comprueba por HTTP cada servicio y sus conexiones a PostgreSQL y Redis.
El resultado JUnit se guarda en `test-results/smoke.xml`.

## Detener

```powershell
docker compose down
```

El volumen de PostgreSQL conserva los datos. No usar `down -v` sobre el entorno local
si se desea conservarlos.

## Organizacion

- src: codigo de los cuatro servicios y comprobacion compartida.
- docker: un Dockerfile por servicio.
- tests: comprobaciones automaticas.
- docs: documentacion y evidencias.
- azure-pipelines.yml: definicion inicial de construccion y pruebas.

## Alcance tecnico

Solo acceso local. PostgreSQL y Redis no publican puertos al equipo.
La base es nueva; el script del entregable 8 aun no esta incorporado.
El entorno de CI es desechable y elimina exclusivamente sus propios volumenes.
CI utiliza docker-compose.ci.yml para evitar publicar puertos y no interferir con el entorno local.

El repositorio también está disponible en Azure Repos, dentro del proyecto Rikeli-Seminario.