import logging
import time

from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from tortoise import exceptions as db_exceptions
from tortoise.expressions import Q

from backend.auth import get_user, generate_token
from backend.models import models, dtos

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello"}


@router.post("/register")
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


@router.post("/upload_image")
async def upload_image(
    file: UploadFile, user: models.User = Depends(get_user)
) -> dtos.StadardResponse:
    contents = await file.read()
    path = f"media/{user.id}_{time.time_ns()}.png"
    logging.error(f"new file created {path}")
    with open(path, "wb") as f:
        f.write(contents)
    await models.Image.create(user=user, path=path)
    logging.error(await models.Image.all())
    return dtos.StadardResponse(message="success")


@router.get("/get_image/{image_id}")
async def get_image(
    image_id: int, user: models.User = Depends(get_user)
) -> FileResponse:
    path = (await models.Image.get(id=image_id)).path
    return FileResponse(path=path)


@router.get("/feed")
async def get_people(user: models.User = Depends(get_user)) -> dtos.UserList:
    current_user_swipes = (
        await models.Swipe.all().prefetch_related("subject").filter(swiper_id=user.id)
    )
    # TODO this is too slow
    swiped_users = [swipe.subject.id for swipe in current_user_swipes]
    users = models.User.exclude(id=user.id, id__in=swiped_users).limit(10)
    return dtos.UserList(users=await users)


@router.get("/matches")
async def matches(user: models.User = Depends(get_user)) -> list[dtos.PublicUser]:
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


@router.get("/me")
async def get_me(user: models.User = Depends(get_user)) -> dtos.PublicUser:
    return dtos.PublicUser.from_orm(user)


@router.post("/tag", status_code=200)
async def add_tags(user: models.User = Depends(get_user)) -> dtos.StadardResponse:
    return dtos.StadardResponse(message="success")


@router.post("/like")
async def like(
    subject: int,
    user: models.User = Depends(get_user),
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
    except db_exceptions.DoesNotExist:
        pass
    return dtos.StadardResponse(message="success")


@router.post("/dislike")
async def dislike(
    subject: int,
    user: models.User = Depends(get_user),
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
