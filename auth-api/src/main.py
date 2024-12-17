import uvicorn
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics

from api.v1 import views
from core.logger import APILoggingMiddleware

app = FastAPI(title="Auth-API")

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.add_middleware(APILoggingMiddleware)
app.include_router(views.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
