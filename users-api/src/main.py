from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.routes.users import router as users_router
from core.config.settings import settings

app = FastAPI(
    title="Users API",
    description="API for managing users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)

Instrumentator().instrument(app).expose(app)
