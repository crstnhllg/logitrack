from pydantic import BaseModel, field_serializer
from datetime import datetime

class BaseModelWithDateFormatting(BaseModel):
    @field_serializer("*", when_used="json")
    def serialize_datetime(self, value, _info):
        if isinstance(value, datetime):
            return value.strftime("%b %d, %Y %I:%M %p")
        return value