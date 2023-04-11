from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE INT USING "birth_date"::INT;
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE INT USING "birth_date"::INT;
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE INT USING "birth_date"::INT;
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE INT USING "birth_date"::INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE VARCHAR(255) USING "birth_date"::VARCHAR(255);
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE VARCHAR(255) USING "birth_date"::VARCHAR(255);
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE VARCHAR(255) USING "birth_date"::VARCHAR(255);
        ALTER TABLE "user" ALTER COLUMN "birth_date" 
        TYPE VARCHAR(255) USING "birth_date"::VARCHAR(255);"""
