from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime, date


class RecordSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=30)
    last_name: str | None = Field(min_length=0, max_length=30)
    email: EmailStr | None
    birthday: date | None = Field()
    notes: str | None = Field(min_length=0, max_length=150)


class RecordUpdateSchema(RecordSchema):
    pass


class RecordResponseSchema(BaseModel):
    id: int = 1
    first_name: str = "John"
    last_name: str | None = 'Doe'
    email: str | None
    birthday: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class UserDBSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str = Field(min_length=3, max_length=30)
    pwd_hash: str = Field(min_length=3, max_length=255)
    avatar: str | None = Field(min_length=3, max_length=255, default=None)
    refresh_token: str | None = Field(
        min_length=3, max_length=255, default=None)

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class EmailSchema(BaseModel):
    email: EmailStr
