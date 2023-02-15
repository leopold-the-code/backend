from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import APIKeyHeader
from base64 import b64encode
from secrets import token_bytes

from tortoise import exceptions
from backend.db import setup_db
from backend.models import models, dtos

token_lenght = 64


app = FastAPI()
setup_db(app)


async def auth(
    token: str | None = Depends(APIKeyHeader(name="X-Token", auto_error=False))
) -> models.User:
    try:
        current_user = await models.User.get(token=token)
    except exceptions.DoesNotExist:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return current_user


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello"}


@app.post("/register")
async def register(user: dtos.RegisterUser) -> dtos.TokenResponse:
    token = generate_token()
    await models.User.create(
        email=user.email,
        name=user.name,
        surname=user.surname,
        description=user.description,
        birth_date=user.birth_date,
        password=user.password,
        token=token,
    )
    print(await models.User.all())
    return dtos.TokenResponse(token=token)


@app.get("/feed")
async def get_people(user: models.User = Depends(auth)) -> dtos.UserList:
    person = dtos.PublicUser(
        id=0,
        email="test",
        name="test",
        surname="test",
        description="test",
        birth_date="test",
    )
    return dtos.UserList(users=[person] * 10)


@app.get("/me")
async def get_me(user: models.User = Depends(auth)) -> dtos.PublicUser:
    return dtos.PublicUser.from_orm(user)


@app.post("/tag", status_code=200)
async def add_tags(user: models.User = Depends(auth)) -> dtos.StadardResponse:
    return dtos.StadardResponse(message="success")


@app.post("/like")
async def like(user: models.User = Depends(auth)) -> dtos.StadardResponse:
    return dtos.StadardResponse(message="success")


@app.post("/dislike")
async def dislike(user: models.User = Depends(auth)) -> dtos.StadardResponse:
    return dtos.StadardResponse(message="success")


def generate_token() -> str:
    token_b = token_bytes(token_lenght)
    return b64encode(token_b).decode("ascii")
