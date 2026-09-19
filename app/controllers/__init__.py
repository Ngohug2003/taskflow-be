from app.controllers.public import public_router
from app.controllers.admin import admin_router
from app.controllers.auth_controller import auth_router
from app.controllers.user_controller import user_router
from app.controllers.workspace_controller import workspace_router

# Đảm bảo lệnh 'from controllers import *' sẽ lấy được các biến này
__all__ = ["public_router", "admin_router", "auth_router", "user_router", "workspace_router"]

