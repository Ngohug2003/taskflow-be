from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, field_serializer, model_validator
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def check_non_space_if_provided(cls, values):
        """
        Validate that all string fields (if provided) are not only whitespace.
        """
        if not isinstance(values, dict):
            # For model_dump Output
            return values

        for field_name, value in values.items():
            if isinstance(value, str) and value != "" and not value.strip():
                raise ValueError(f"Field '{field_name}' cannot contain only spaces.")
        return values

class BaseOutput(BaseSchema):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: Optional[datetime], _info):
        if not value:
            return None
        vn_time = value.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        return vn_time.strftime("%H:%M:%S %d/%m/%Y")