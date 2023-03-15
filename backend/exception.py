from fastapi.responses import JSONResponse


async def not_exist_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )
