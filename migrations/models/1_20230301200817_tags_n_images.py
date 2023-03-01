from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" VARCHAR(255) NOT NULL
);;
        ALTER TABLE "user" DROP COLUMN "surname";
        CREATE TABLE "tag_user" (
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "tag_user";
        ALTER TABLE "user" ADD "surname" VARCHAR(255);
        DROP TABLE IF EXISTS "tag";"""
