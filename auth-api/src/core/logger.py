import logging
from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

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

        process_time = (time.time() - start_time) * 1000

        extra = {
            "method": request.method,
            "url": request.url,
            "status_code": response.status_code,
            "process_time": process_time,
        }

        api_logger.info('API Request', extra=extra)

        return response
