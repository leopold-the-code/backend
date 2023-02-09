from fastapi import FastAPI, Request, status, Response
from pydantic import BaseModel
from datetime import date
from base64 import b64decode, b64encode
from secrets import token_bytes

token_lenght = 10


class User(BaseModel):
    name: str
    surname: str
    description: str
    birth_date: str
    email: str
    password: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello"}


@app.post("/register")
async def register(user: User):
    return {"token": generate_token()}


@app.get("/people")
async def get_people(request: Request, response: Response):
    is_authorized = check_token(request)
    if not is_authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    a = {"id": 0, "name": "test", "surname": "test", "description": "test"}
    list = []
    for i in range(10):
        list.append(a)
    return {"users": list}


@app.post("/tag", status_code=200)
async def add_tags(request: Request, response: Response):
    is_authorized = check_token(request)
    if not is_authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return


@app.post("/like")
async def like(request: Request, response: Response):
    is_authorized = check_token(request)
    if not is_authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return


@app.post("/dislike")
async def dislike(request: Request, response: Response):
    is_authorized = check_token(request)
    if not is_authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return


def generate_token() -> str:
    token_b = token_bytes(token_lenght)
    return b64encode(token_b).decode("ascii")


def check_token(request: Request) -> bool:
    token = request.headers.get("X-Token")
    return token is not None and token != ""
