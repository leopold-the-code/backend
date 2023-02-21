from backend import models


async def create_demousers():
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
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 3",
        surname="DemoSurname",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken3",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 4",
        surname="DemoSurname",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken4",
    )
    await models.User.get_or_create(
        email="email@example.com",
        name="DemoName 5",
        surname="DemoSurname",
        description="Description",
        birth_date="2001",
        password="12345",
        token="demotoken5",
    )
