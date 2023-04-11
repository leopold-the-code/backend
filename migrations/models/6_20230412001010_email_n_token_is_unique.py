from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_user_email_1b4f1c" ON "user" ("email");
        CREATE UNIQUE INDEX "uid_user_token_feec3b" ON "user" ("token");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_user_token_feec3b";
        DROP INDEX "idx_user_email_1b4f1c";"""
