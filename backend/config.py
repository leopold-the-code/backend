import logging
from pydantic import BaseSettings


logger = logging.Logger(name="APP", level=logging.DEBUG)

formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite://:memory:"
    generate_schemas: bool = True
    site_url: str = "http://127.0.0.1:8000"

    class Config:
        case_sensitive = False
        env_file = ".env"


settings = Settings()


TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["backend.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
