from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'auth_request_total',
    'Total number of requests to this service',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'auth_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

LOGIN_ATTEMPTS = Counter(
    'auth_login_attempts_total',
    'Total number of login attempts',
    ['status']
)
