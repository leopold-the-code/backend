from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    description: str
    birth_date: int


class RegisterUser(UserBase):
    password: str

    class Config:
        orm_mode = True


class PublicUser(UserBase):
    id: int
    tags: list[str]
    images: list[str]

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: list[PublicUser]


class TokenResponse(BaseModel):
    token: str


class StadardResponse(BaseModel):
    message: str
