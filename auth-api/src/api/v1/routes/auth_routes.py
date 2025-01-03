from fastapi import APIRouter, Depends, HTTPException, Header
from core.dto.auth_dto import LoginRequest, TokenResponse, RefreshTokenRequest
from api.v1.controllers.auth_controller import AuthController
from core.dependencies.dependencies import get_auth_controller
from core.exceptions.auth_exceptions import AuthException

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        credentials: LoginRequest,
        controller: AuthController = Depends(get_auth_controller)
):
    try:
        return await controller.login(credentials)
    except AuthException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        request: RefreshTokenRequest,
        controller: AuthController = Depends(get_auth_controller)
):
    try:
        return await controller.refresh_token(request.refresh_token)
    except AuthException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/validate")
async def validate_token(
        controller: AuthController = Depends(get_auth_controller),
        authorization: str | None = Header(default=None, alias="Authorization")
):
    try:
        return await controller.validate_token(authorization)
    except AuthException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
