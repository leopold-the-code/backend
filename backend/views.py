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


class UpdateUser(BaseModel):
    email: EmailStr | None
    name: str | None
    description: str | None
    birth_date: int | None
    password: str | None
    latitude: float | None
    longitude: float | None
    tags: list[str] | None


class PublicUser(UserBase):
    id: int
    tags: list[str]
    images: list[int]

    class Config:
        orm_mode = True


class MeUser(PublicUser):
    latitude: float
    longitude: float


class UserList(BaseModel):
    users: list[PublicUser]


class TokenResponse(BaseModel):
    token: str


class StandardResponse(BaseModel):
    message: str
