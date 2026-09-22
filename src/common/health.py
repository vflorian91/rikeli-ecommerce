import os
import psycopg
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app(service: str) -> FastAPI:
    app = FastAPI(title=f"Rikeli - {service}", version="0.1.0")

    @app.get("/health", tags=["Infraestructura"])
    def health():
        checks = {}
        try:
            with psycopg.connect(host="postgres", dbname=os.environ["POSTGRES_DB"],
                                 user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"],
                                 connect_timeout=3) as connection:
                connection.execute("SELECT 1").fetchone()
            checks["postgres"] = "ok"
        except (psycopg.Error, KeyError):
            checks["postgres"] = "error"
        try:
            cache = redis.Redis(host="redis", socket_connect_timeout=3, socket_timeout=3)
            cache.ping()
            cache.close()
            checks["redis"] = "ok"
        except redis.RedisError:
            checks["redis"] = "error"
        healthy = all(value == "ok" for value in checks.values())
        return JSONResponse({"service": service, "status": "ok" if healthy else "error", "dependencies": checks},
                            status_code=200 if healthy else 503)
    return app
