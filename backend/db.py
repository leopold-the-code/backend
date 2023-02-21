from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from backend.config import settings


def setup_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={"models": ["backend.models"]},
        generate_schemas=settings.generate_schemas,
    )
