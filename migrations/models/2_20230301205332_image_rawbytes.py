from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "image" ADD "rawbytes" BYTEA NOT NULL;
        ALTER TABLE "image" DROP COLUMN "path";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "image" ADD "path" VARCHAR(500) NOT NULL;
        ALTER TABLE "image" DROP COLUMN "rawbytes";"""
