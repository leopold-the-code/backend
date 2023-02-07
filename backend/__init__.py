from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    login: str
    password: str

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello"} 

@app.post("/register")
async def register(user: User):
    return user

@app.get("/people")
async def get_people():
    return {"message": "people suggestions"}


