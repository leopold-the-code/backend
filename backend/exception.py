from __init__ import app
from fastapi import Request
from tortoise import exceptions as db_exceptions
from fastapi.responses import JSONResponse


@app.exception_handler(db_exceptions.DoesNotExist)
async def not_exist_exception_handler(
    requset: Request, exc: db_exceptions.DoesNotExist
):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )
