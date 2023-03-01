from backend import models


async def create_demousers() -> None:
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 2",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken2",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 3",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken3",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 4",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken4",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 5",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken5",
    )
