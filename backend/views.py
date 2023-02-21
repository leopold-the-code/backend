from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    name: str
    surname: str
    description: str
    birth_date: str


class RegisterUser(UserBase):
    password: str

    class Config:
        orm_mode = True


class PublicUser(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: list[PublicUser]


class TokenResponse(BaseModel):
    token: str


class StadardResponse(BaseModel):
    message: str
