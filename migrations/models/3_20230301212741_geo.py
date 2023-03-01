from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "longitude" DOUBLE PRECISION;
        ALTER TABLE "user" ADD "latitude" DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "longitude";
        ALTER TABLE "user" DROP COLUMN "latitude";"""
