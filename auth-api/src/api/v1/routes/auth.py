from fastapi import APIRouter

from ..controllers.auth_controller import AuthController
from ..schemas import LoginData, TokenResponse

router = APIRouter()

router.add_api_route(
    "/login",
    AuthController.login,
    methods=["POST"],
    response_model=TokenResponse
)

router.add_api_route(
    "/validate",
    AuthController.validate_token,
    methods=["POST"]
) 