from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import AllMessages
from app.models.base import BaseDbModel
from app.utils.custom_exception import CustomException
from app.utils.string_helpers import StringHelper

class BaseService:

    @staticmethod
    def custom_response(data=None, status_code=200, message=None, errors=None, internal_code=None) -> JSONResponse:
        if internal_code is None:
            internal_code = status_code
        response = {
            'status': {
                'code': internal_code,
                'message': message if message is not None else AllMessages.HTTP_MESSAGES.get(internal_code, "Unknown Message")
            },
            'data': data
        }

        if data is not None:
            response['data'] = data
        if errors is not None:
            response['errors'] = errors

        return JSONResponse(status_code=status_code, content=jsonable_encoder(response))

    @staticmethod
    async def generate_unique_slug(db_session: AsyncSession, name: str, model: type[BaseDbModel], column: str,
                                   id_to_exclude: int | None = None,
                                   id_field: str = "id"):
        if not hasattr(model, column):
            raise CustomException(status_code=500, message=f"The model does not have a column named '{column}'")
        base_slug = StringHelper.to_slug(name)
        slug = base_slug
        counter = 2
        while True:
            query = select(model).where(getattr(model, column, None) == slug)
            if id_to_exclude:
                query = query.where(getattr(model, id_field, None) != id_to_exclude)
            result = await db_session.execute(query)
            existing = result.scalars().first()
            if not existing:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1
