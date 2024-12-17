import logging
from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.metrics import REQUEST_LATENCY, REQUEST_COUNT

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

api_formatter = logging.Formatter(
    '%(asctime)s - %(method)s - %(url)s - %(status_code)s - %(process_time).2fms'

)

api_handler = logging.FileHandler(LOG_DIR / 'api.log', encoding='utf-8')
api_handler.setFormatter(api_formatter)

api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO)
api_logger.addHandler(api_handler)


class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time

        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        extra = {
            'method': request.method,
            'url': request.url.path,
            'status_code': response.status_code,
            'process_time': duration * 1000
        }
        api_logger.info('API Request', extra=extra)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
