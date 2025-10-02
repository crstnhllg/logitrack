from pydantic import BaseModel, Field, constr, field_validator
from app.schemas.base import BaseModelWithDateFormatting
from datetime import datetime
from typing import Optional


class OrderRequest(BaseModel):
    destination: constr(min_length=3) = Field(examples=['Manila'])
    size: constr(min_length=1, strip_whitespace=True) = Field(examples=['xs', 's', 'm', 'l', 'xl'])
    priority: bool = Field(examples=[True, False])
    delivery_window_start: str = Field(examples=['2025-12-12 10:00'])
    delivery_window_end: str = Field(examples=['2025-12-15 10:00'])
    status: constr(min_length=3, strip_whitespace=True) = Field(examples=['pending'])
    vehicle_id: Optional[int] = Field(None, gt=0, examples=[1])

    @field_validator("delivery_window_start", "delivery_window_end")
    def parse_datetime(cls, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Date must be in format YYYY-MM-DD HH:MM")


class OrderStatusRequest(BaseModel):
    order_status: constr(min_length=3, strip_whitespace=True) = Field(examples=['completed'])


class OrderResponse(BaseModelWithDateFormatting):
    id: int
    updated_at: datetime
    destination: str
    size: str
    priority: bool
    delivery_window_start: datetime
    delivery_window_end: datetime
    status: str
    vehicle_id: Optional[int]

    class Config:
        from_attributes = True