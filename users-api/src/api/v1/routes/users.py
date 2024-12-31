from fastapi import APIRouter

from ..controllers.users import UsersController

router = APIRouter(
    prefix="/api/v1",
    tags=["Users"],
)

router.add_api_route("/health", UsersController.health, methods=["GET"])
router.add_api_route("/health/db", UsersController.db_health_check, methods=["GET"])

router.add_api_route("/me", UsersController.get_current_user_profile, methods=["GET"])
router.add_api_route("/update_fullname", UsersController.update_user_fullname, methods=["PATCH"])
router.add_api_route("/update_email", UsersController.update_user_email, methods=["PATCH"])
router.add_api_route("/delete", UsersController.delete_user, methods=["DELETE"])
router.add_api_route("/create", UsersController.create_user, methods=["POST"])

router.add_api_route("/verify-email", UsersController.verify_email, methods=["GET"])
router.add_api_route("/password-forgot", UsersController.request_password_reset, methods=["POST"])
router.add_api_route("/password-reset", UsersController.reset_password, methods=["POST"])

router.add_api_route("/admin/users", UsersController.list_users, methods=["GET"])
router.add_api_route("/admin/users/{user_id}", UsersController.get_user, methods=["GET"])
