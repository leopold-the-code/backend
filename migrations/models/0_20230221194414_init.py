from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255),
    "name" VARCHAR(255),
    "surname" VARCHAR(255),
    "description" VARCHAR(255),
    "birth_date" VARCHAR(255),
    "password" VARCHAR(255),
    "token" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "image" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "path" VARCHAR(500) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "match" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "initializer_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "responder_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "swipe" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "side" BOOL NOT NULL,
    "subject_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "swiper_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
