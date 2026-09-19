from fastapi import APIRouter
from app.controllers.admin.user_controller import user_router

# Khởi tạo Admin Aggregator Router với Tags cố định
admin_router = APIRouter(tags=["Admin"])

# Gộp các router quản trị
admin_router.include_router(user_router)
