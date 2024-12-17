import uvicorn
from fastapi import FastAPI
from api.v1 import views
from core.logger import APILoggingMiddleware

app = FastAPI(title="Auth-API")

app.add_middleware(APILoggingMiddleware)

app.include_router(views.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
