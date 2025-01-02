from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__("Неверные учетные данные")


class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__("Токен истек")


class InactiveUserException(AuthException):
    def __init__(self):
        super().__init__("Пользователь неактивен")


class UnverifiedEmailException(AuthException):
    def __init__(self):
        super().__init__("Email не подтвержден")
