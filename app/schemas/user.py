from pydantic import BaseModel, Field, constr, EmailStr


class CreateUserRequest(BaseModel):
    username: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["john_doe"]
    )
    email: EmailStr = Field(examples=["john_doe@example.com"])
    role: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["admin/driver"]
    )
    password: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["12345"]
    )


class UpdateUserRequest(BaseModel):
    old_password: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["old_password"]
    )
    new_password: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["new_password"]
    )


class UpdateRoleRequest(BaseModel):
    role: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["admin/driver"]
    )


class PasswordRequest(BaseModel):
    password: constr(min_length=3, max_length=20, strip_whitespace=True) = Field(
        examples=["12345"]
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True
