from backend import models


async def create_demousers() -> None:
    user1, created = await models.User.get_or_create(
        email="email1@example.com",
        name="DemoName",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken",
        latitude=43.23,
        longitude=76.91,
    )
    await models.User.get_or_create(
        email="email2@example.com",
        name="DemoName 2",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken2",
    )
    await models.User.get_or_create(
        email="email3@example.com",
        name="DemoName 3",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken3",
    )
    await models.User.get_or_create(
        email="email4@example.com",
        name="DemoName 4",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken4",
    )
    user5, _ = await models.User.get_or_create(
        email="email5@example.com",
        name="DemoName 5",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken5",
        latitude=43.22,
        longitude=76.84,
    )
    tag1, _ = await models.Tag.get_or_create(value="chess")
    tag2, _ = await models.Tag.get_or_create(value="board")
    tag3, _ = await models.Tag.get_or_create(value="video")
    tag4, _ = await models.Tag.get_or_create(value="film")
    tag5, _ = await models.Tag.get_or_create(value="music")

    await user1.tag_objects.add(tag1)
    await user1.tag_objects.add(tag2)
    await user1.tag_objects.add(tag3)

    await user5.tag_objects.add(tag3)
    await user5.tag_objects.add(tag4)
    await user5.tag_objects.add(tag5)

    await models.Swipe.get_or_create(swiper=user1, subject=user5, side=True)

    await models.Match.get_or_create(initializer=user1, responder=user5)
