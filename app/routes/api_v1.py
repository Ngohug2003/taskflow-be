from fastapi import APIRouter
from app.controllers import *
from app.utils.configs import project_settings

api_v1 = APIRouter(prefix=project_settings.API_PREFIX)

# Include các router aggregator, tags sẽ được lấy từ file __init__ của controller
api_v1.include_router(public_router, prefix='/public')
api_v1.include_router(auth_router, prefix='/auth')
api_v1.include_router(user_router, prefix='/users')
api_v1.include_router(admin_router, prefix='/admin')
api_v1.include_router(workspace_router, prefix='/workspaces')

