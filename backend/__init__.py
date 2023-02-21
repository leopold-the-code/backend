from fastapi import FastAPI

from backend.db import setup_db
from backend.routes import router
from backend.app_events import create_demousers


app = FastAPI()
setup_db(app)
app.include_router(router)
app.add_event_handler("startup", create_demousers)
