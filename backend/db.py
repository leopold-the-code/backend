from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


def setup_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url="sqlite://:memory:",
        modules={"models": ["backend.models"]},
        generate_schemas=True,
    )
