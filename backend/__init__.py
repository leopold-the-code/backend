import logging
import time
from fastapi import FastAPI, status, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from base64 import b64encode
from secrets import token_bytes

from tortoise import exceptions
from tortoise.expressions import Q
from backend.db import setup_db
from backend.models import models, dtos

token_lenght = 64


app = FastAPI()
setup_db(app)


@app.on_event("startup")
async def startup_event():
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName",
        surname="DemoSurname",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 2",
        surname="DemoSurname",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken2",
    )


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


@app.post("/upload_image")
async def upload_image(
    file: UploadFile, user: models.User = Depends(auth)
) -> dtos.StadardResponse:
    contents = await file.read()
    path = f"media/{user.id}_{time.time_ns()}.png"
    logging.error(f"new file created {path}")
    with open(path, "wb") as f:
        f.write(contents)
    await models.Image.create(user=user, path=path)
    logging.error(await models.Image.all())
    return dtos.StadardResponse(message="success")


@app.get("/get_image/{image_id}")
async def get_image(image_id: int, user: models.User = Depends(auth)) -> FileResponse:
    path = (await models.Image.get(id=image_id)).path
    return FileResponse(path=path)


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


@app.get("/matches")
async def matches(user: models.User = Depends(auth)) -> list[dtos.PublicUser]:
    matches: list[models.Match] = (
        await models.Match.all()
        .prefetch_related("initializer", "responder")
        .filter(Q(initializer=user) | Q(responder=user))
    )

    companions: list[models.User] = [
        match.responder if match.responder.id != user.id else match.initializer
        for match in matches
    ]
    return companions


@app.get("/me")
async def get_me(user: models.User = Depends(auth)) -> dtos.PublicUser:
    return dtos.PublicUser.from_orm(user)


@app.post("/tag", status_code=200)
async def add_tags(user: models.User = Depends(auth)) -> dtos.StadardResponse:
    return dtos.StadardResponse(message="success")


@app.post("/like")
async def like(
    subject: int,
    user: models.User = Depends(auth),
) -> dtos.StadardResponse:
    if subject == user.id:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't like yourself",
        )

    if await models.Swipe.filter(swiper=user, subject_id=subject).count() != 0:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't evaluate same user more than once",
        )
    await models.Swipe.create(swiper=user, subject_id=subject, side=True)
    print(f"New swipe to right from {user.id} to {subject}")

    try:
        first_swipe = await models.Swipe.get(swiper_id=subject, subject=user)
        if first_swipe.side:
            await models.Match.create(initializer_id=subject, responder=user)
            print("New match")
        else:
            print("Oh, this is not mutual")
    except exceptions.DoesNotExist:
        pass
    return dtos.StadardResponse(message="success")


@app.post("/dislike")
async def dislike(
    subject: int,
    user: models.User = Depends(auth),
) -> dtos.StadardResponse:
    if subject == user.id:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't dislike yourself",
        )

    if await models.Swipe.filter(swiper=user, subject_id=subject).count() != 0:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't evaluate same user more than once",
        )

    await models.Swipe.create(swiper=user, subject_id=subject, side=False)
    print(f"New swipe to left from {user.id} to {subject}")
    return dtos.StadardResponse(message="success")


def generate_token() -> str:
    token_b = token_bytes(token_lenght)
    return b64encode(token_b).decode("ascii")
