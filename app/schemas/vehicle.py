from pydantic import BaseModel, Field, constr
from app.schemas.base import BaseModelWithDateFormatting
from datetime import datetime


class VehicleRequest(BaseModel):
    license_plate: constr(min_length=3, max_length=15, strip_whitespace=True) = Field(examples=['abc123'])
    vehicle_type: constr(min_length=3, max_length=15, strip_whitespace=True) = Field(examples=['van'])
    capacity_kg: int = Field(gt=0, examples=['15'])
    vehicle_status: constr(min_length=3, max_length=15, strip_whitespace=True) = Field(examples=['available'])
    driver_id: int = Field(gt=0, examples=['1'])


class VehicleStatusRequest(BaseModel):
    vehicle_status: constr(min_length=3, max_length=15, strip_whitespace=True) = Field(examples=['available'])


class VehicleDriverRequest(BaseModel):
    driver_id: int = Field(gt=0, examples=[1])


class VehicleResponse(BaseModelWithDateFormatting):
    id: int
    updated_at: datetime
    license_plate: str
    type: str
    capacity_kg: int
    status: str
    driver_id: int

    class Config:
        from_attributes = True
