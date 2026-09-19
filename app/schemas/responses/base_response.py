from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class GenericResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    error_code: str = "SUCCESS"
    data: Optional[T] = None
