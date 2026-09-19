from fastapi import APIRouter

# Khởi tạo Public Aggregator Router với Tags cố định
public_router = APIRouter(tags=["Public"])

# Sau này include các router con vào đây
# from .news_controller import news_router
# public_router.include_router(news_router)