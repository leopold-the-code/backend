from fastapi import FastAPI, Request, status, Response, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from base64 import b64decode, b64encode
from secrets import token_bytes

from backend.db import setup_db
from backend import models

token_lenght = 64


class User(BaseModel):
    name: str
    surname: str
    description: str
    birth_date: str
    email: str
    password: str


class TokenResponse(BaseModel):
    token: str


app = FastAPI()
setup_db(app)


def auth(request: Request):
    is_authorized = check_token(request)
    if not is_authorized:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    # TODO return authorized user in future


@app.get("/")
async def root():
    return {"message": "hello"}


@app.post("/register")
async def register(user: User) -> TokenResponse:
    await models.User.create(email="example@example.org")
    print(await models.User.all())
    return TokenResponse(token=generate_token())


@app.get("/feed")
async def get_people(user=Depends(auth)):
    a = {"id": 0, "name": "test", "surname": "test", "description": "test"}
    list = []
    for _ in range(10):
        list.append(a)
    return {"users": list}


@app.post("/tag", status_code=200)
async def add_tags(user=Depends(auth)):
    pass


@app.post("/like")
async def like(user=Depends(auth)):
    pass


@app.post("/dislike")
async def dislike(user=Depends(auth)):
    pass


def generate_token() -> str:
    token_b = token_bytes(token_lenght)
    return b64encode(token_b).decode("ascii")


def check_token(request: Request) -> bool:
    token = request.headers.get("X-Token")
    return token is not None and token != ""
