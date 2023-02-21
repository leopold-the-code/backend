import time

from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from tortoise import exceptions as db_exceptions
from tortoise.expressions import Q
from backend import views

from backend.auth import get_user, generate_token
from backend.models import models
from backend.config import logger

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello"}


@router.post("/register")
async def register(user: views.RegisterUser) -> views.TokenResponse:
    token = generate_token()
    user = await models.User.create(
        email=user.email,
        name=user.name,
        surname=user.surname,
        description=user.description,
        birth_date=user.birth_date,
        password=user.password,
        token=token,
    )
    logger.info(f"New user with id {user.id} created")
    return views.TokenResponse(token=token)


@router.post("/upload_image")
async def upload_image(
    file: UploadFile, user: models.User = Depends(get_user)
) -> views.StadardResponse:
    contents = await file.read()  # TODO don't read entire file
    path = f"media/{user.id}_{time.time_ns()}.png"
    with open(path, "wb") as f:  # TODO buffering
        f.write(contents)
    logger.info(f"File saved at {path}")
    image = await models.Image.create(user=user, path=path)
    logger.info(f"New image with id {image.id}")
    return views.StadardResponse(message="success")


@router.get("/get_image/{image_id}")
async def get_image(
    image_id: int, user: models.User = Depends(get_user)
) -> FileResponse:
    path = (await models.Image.get(id=image_id)).path
    return FileResponse(path=path)


@router.get("/feed")
async def get_people(user: models.User = Depends(get_user)) -> views.UserList:
    current_user_swipes = (
        await models.Swipe.all().prefetch_related("subject").filter(swiper_id=user.id)
    )
    # TODO this is too slow
    swiped_users = [swipe.subject.id for swipe in current_user_swipes]
    users = models.User.exclude(id=user.id, id__in=swiped_users).limit(10)
    return views.UserList(users=await users)


@router.get("/matches")
async def matches(user: models.User = Depends(get_user)) -> list[views.PublicUser]:
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
async def get_me(user: models.User = Depends(get_user)) -> views.PublicUser:
    return views.PublicUser.from_orm(user)


@router.post("/tag", status_code=200)
async def add_tags(user: models.User = Depends(get_user)) -> views.StadardResponse:
    return views.StadardResponse(message="success")


@router.post("/like")
async def like(
    subject: int,
    user: models.User = Depends(get_user),
) -> views.StadardResponse:
    if subject == user.id:
        logger.error("Client is trying to like himself")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't like yourself",
        )

    if await models.Swipe.filter(swiper=user, subject_id=subject).count() != 0:
        logger.error("Client is trying to evaluate user more than once")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't evaluate same user more than once",
        )
    await models.Swipe.create(swiper=user, subject_id=subject, side=True)
    logger.info(f"New swipe to right from {user.id} to {subject}")

    try:
        first_swipe = await models.Swipe.get(swiper_id=subject, subject=user)
        if first_swipe.side:
            await models.Match.create(initializer_id=subject, responder=user)
            logger.info("New match")
        else:
            logger.info("Oh, this is not mutual")
    except db_exceptions.DoesNotExist:
        pass
    return views.StadardResponse(message="success")


@router.post("/dislike")
async def dislike(
    subject: int,
    user: models.User = Depends(get_user),
) -> views.StadardResponse:
    if subject == user.id:
        logger.error("Client is trying to dislike himself")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't dislike yourself",
        )

    if await models.Swipe.filter(swiper=user, subject_id=subject).count() != 0:
        logger.error("Client is trying to evaluate user more than once")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="you can't evaluate same user more than once",
        )

    await models.Swipe.create(swiper=user, subject_id=subject, side=False)
    logger.info(f"New swipe to left from {user.id} to {subject}")
    return views.StadardResponse(message="success")
