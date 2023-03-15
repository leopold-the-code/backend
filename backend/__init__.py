from fastapi import FastAPI
from tortoise import exceptions as db_exceptions

from backend.db import setup_db
from backend.exception import not_exist_exception_handler
from backend.routes import router
from backend.app_events import create_demousers
from backend.ws import router as ws_router


app = FastAPI()
setup_db(app)
app.include_router(router)
app.include_router(ws_router)
app.add_event_handler("startup", create_demousers)

app.add_exception_handler(db_exceptions.DoesNotExist, not_exist_exception_handler)
