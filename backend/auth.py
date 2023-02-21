from base64 import b64encode
from secrets import token_bytes

from fastapi import status, Depends, HTTPException
from fastapi.security import APIKeyHeader
from tortoise import exceptions as db_exceptions

from backend import models


token_length = 64


async def get_user(
    token: str | None = Depends(APIKeyHeader(name="X-Token", auto_error=False))
) -> models.User:
    try:
        current_user = await models.User.get(token=token)
    except db_exceptions.DoesNotExist:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return current_user


def generate_token() -> str:
    token_b = token_bytes(token_length)
    return b64encode(token_b).decode("ascii")
