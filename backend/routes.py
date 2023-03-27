from datetime import datetime

from pydantic import EmailStr

from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, Query
from fastapi.responses import Response
from tortoise import exceptions as db_exceptions
from tortoise.expressions import Q
from backend import views

from backend.auth import get_user, get_public_user, generate_token
from backend import models
from backend.config import logger


router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello"}


@router.post("/register")
async def register(user: views.RegisterUser) -> views.TokenResponse:
    token = generate_token()
    created_user = await models.User.create(
        email=user.email,
        name=user.name,
        description=user.description,
        birth_date=user.birth_date,
        password=user.password,
        token=token,
    )
    logger.info(f"New user with id {created_user.name} created")
    return views.TokenResponse(token=token)


@router.post("/login")
async def login(email: EmailStr, password: str) -> views.TokenResponse:
    user = await models.User.get(email=email, password=password)
    return views.TokenResponse(token=user.token)


@router.post("/upload_image")
async def upload_image(
    file: UploadFile, user: models.User = Depends(get_user)
) -> views.StandardResponse:
    content = await file.read()
    image = await models.Image.create(user=user, rawbytes=content)
    logger.info(f"New image with id {image.id}")
    return views.StandardResponse(message="success")


@router.delete("/delete_image/{image_id}")
async def delete_image(
    image_id: int, user: models.User = Depends(get_user)
) -> views.StandardResponse:
    image = await models.Image.get(id=image_id, user=user)
    await image.delete()
    return views.StandardResponse(message="success")


@router.get("/get_image/{image_id}")
async def get_image(image_id: int, user: models.User = Depends(get_user)) -> Response:
    content = (await models.Image.get(id=image_id)).rawbytes
    return Response(content=content, media_type="image/png")


@router.get("/feed")
async def get_people(user: models.User = Depends(get_user)) -> views.UserList:
    current_user_swipes = (
        await models.Swipe.all().prefetch_related("subject").filter(swiper_id=user.id)
    )
    # models.Swipe.all().prefetch_related("subject").filter(swiper_id=user.id).sql()
    # TODO this is too slow
    swiped_users = [swipe.subject.id for swipe in current_user_swipes]
    # models.User.raw("SELECT x, y FROM user ")
    users = (
        models.User.exclude(id=user.id, id__in=swiped_users)
        .prefetch_related("tag_objects", "image_objects")
        .limit(10)
    )

    return views.UserList(users=await users)


@router.get("/matches")
async def matches(user: models.User = Depends(get_user)) -> list[views.PublicUser]:
    matches: list[models.Match] = (
        await models.Match.all()
        .prefetch_related(
            "responder__tag_objects",
            "responder__image_objects",
            "initializer__tag_objects",
            "initializer__image_objects",
        )
        .filter(Q(initializer=user) | Q(responder=user))
    )

    companions: list[views.PublicUser] = [
        views.PublicUser.from_orm(
            match.responder if match.responder.id != user.id else match.initializer
        )
        for match in matches
    ]
    return companions


@router.get("/me")
async def get_me(user: models.User = Depends(get_public_user)) -> views.PublicUser:
    return views.PublicUser.from_orm(user)


@router.post("/me")
async def update_me(
    update_data: views.UpdateUser, user: models.User = Depends(get_user)
) -> views.StandardResponse:
    delete_tags = await user.tag_objects.all()
    delete_tags_values = set([tag.value for tag in delete_tags])
    if update_data.tags is not None:
        for tag_value in update_data.tags:
            tag, created = await models.Tag.get_or_create(value=tag_value)
            if created:
                logger.info("New tag created")
            await tag.user.add(user)

            if tag_value in delete_tags_values:
                delete_tags_values.remove(tag_value)
                logger.info(f"Tag {tag_value} removed from user {user.id}")

        for tag_value in delete_tags_values:
            tag = await models.Tag.get_or_none(value=tag_value)
            if tag is not None:
                logger.info(f"tag {tag_value} deleted from user {user.id}")
                await tag.user.remove(user)

    user.update_from_dict(
        update_data.dict(
            exclude_none=True,
            exclude_defaults=True,
        )
    )
    await user.save()
    return views.StandardResponse(message="success")


@router.get("/profile/{profile_id}")
async def get_profile(
    profile_id: int, user: models.User = Depends(get_user)
) -> views.PublicUser:
    return views.PublicUser.from_orm(
        await models.User.get(id=profile_id).prefetch_related(
            "tag_objects", "image_objects"
        )
    )


@router.post("/tag", status_code=200)
async def add_tag(
    user: models.User = Depends(get_user), tag_value: str = Query()
) -> views.StandardResponse:
    tag, created = await models.Tag.get_or_create(value=tag_value)
    if created:
        logger.info("New tag created")
    await tag.user.add(user)
    return views.StandardResponse(message="success")


@router.post("/like")
async def like(
    subject: int,
    user: models.User = Depends(get_user),
) -> views.StandardResponse:
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
    return views.StandardResponse(message="success")


@router.post("/dislike")
async def dislike(
    subject: int,
    user: models.User = Depends(get_user),
) -> views.StandardResponse:
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
    return views.StandardResponse(message="success")


@router.post("/reset_swipes")
async def reset_swipes(user: models.User = Depends(get_user)) -> views.StandardResponse:
    await models.Swipe.filter(swiper=user).delete()
    return views.StandardResponse(message="success")


@router.get("/messages")
async def get_messages(last_datetime: datetime, user: models.User = Depends(get_user)):
    user_matches = [
        match.id
        for match in await models.Match.filter(Q(initializer=user) | Q(responder=user))
    ]
    messages = await models.Message.filter(
        match__id__in=user_matches, receive_datetime__gt=last_datetime
    )
    return messages


@router.post("/train_nn")
async def train_nn():
    # xs, ys = await ml.load_data()

    xs = []
    ys = []
    # xs = [[22, 22, 5.7796794630746025, 0.3333333333333333]]
    # ys = [[1.0]]

    from random import random

    for _ in range(10000):
        sim = random()
        xs.append([random() * 70, random() * 70, random() * 15, sim])
        ys.append([1.0 if sim > 0.5 else 0])
        # ys.append([1])
    # print(xs)
    # print(ys)
    from torch.utils.data import TensorDataset, DataLoader
    import torch
    from torch import nn

    xs_tensor = torch.tensor(xs, dtype=torch.float32)
    ys_tensor = torch.tensor(ys, dtype=torch.float32)

    # Create a TensorDataset from the tensors
    dataset = TensorDataset(xs_tensor, ys_tensor)

    # Create a DataLoader from the dataset
    dataloader = DataLoader(dataset, batch_size=100)

    device = "cpu"
    print(f"Using {device} device")

    # Define model
    class NeuralNetwork(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear_relu_stack = nn.Sequential(
                nn.Linear(4, 32),
                nn.ReLU(),
                nn.Linear(32, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            x = self.linear_relu_stack(x)
            return x

    model = NeuralNetwork().to(device)
    print(model)

    # loss_fn = nn.BCEWithLogitsLoss()
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

    # train
    def train(dataloader, model, loss_fn, optimizer):
        size = len(dataloader.dataset)
        model.train()
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)
            # print(X)
            # print(y)
            # Compute prediction error
            pred = model(X)

            # print("PRED", pred)
            # print("Y", y)

            loss = loss_fn(pred, y)
            # print("LOSS", loss.item())

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (batch) % 20 == 0:
                loss, current = loss.item(), (batch + 1) * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

    epochs = 25
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train(dataloader, model, loss_fn, optimizer)
        # test(test_dataloader, model, loss_fn)
    print("Done!")

    # torch.save(model.state_dict(), "model.pth")

    model.eval()
    with torch.no_grad():
        output = model.forward(torch.tensor([22.0, 22.0, 5.0, 1.0]))
        print(output)
    model.eval()
    with torch.no_grad():
        output = model.forward(torch.tensor([22.0, 22.0, 5.0, 0.0]))
        print(output)
