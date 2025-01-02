import logging
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics

from api.v1.routes import auth_routes
from core.logger import APILoggingMiddleware
from core.dependencies.dependencies import get_auth_service
from api.v1.services.auth_service import AuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth-API")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")


app.add_middleware(PrometheusMiddleware)
app.add_middleware(APILoggingMiddleware)

app.include_router(auth_routes.router)

app.add_route("/metrics", metrics)

app.dependency_overrides[AuthService] = get_auth_service
