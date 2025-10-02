from pydantic import BaseModel


class MessageResponse(BaseModel):
    status: str
    message: str

    class Config:
        from_attributes = True