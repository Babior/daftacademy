from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from datetime import date, timedelta

fake_users_db = {
    "johndoe": {
        "name": "liza",
        "surname": "podliza",
    },
    "alice": {
        "name": "roma",
        "surname": "svelodrorma",

    },
}

class User(BaseModel):
    id: int
    name: str
    surname: str
    register_date: date
    vaccination_date: date


app = FastAPI()
app.counter = 1


@app.get("/")
def read_root():
    return {"message": "Hello world!"}


@app.api_route("/method/", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def return_method(request: Request) -> JSONResponse:
    """
    Method to return request method.
    : param: request
    : return: request method
    """
    if request.method == "POST":
        return JSONResponse({"method": request.method}, status_code=201)
    return JSONResponse({"method": request.method})


@app.post("/register/{user_id}", status_code=201)
def registration(user: User):
    app.counter += 1
    user.id = app.counter
    d = len(user.name) + len(user.surname)
    user.vaccination_date = user.register_date + timedelta(len(user.name) + len(user.surname))
    return {"id": user.id, "name": user.name, "surname": user.surname, "register_date": user.register_date, "vaccination_date": user.vaccination_date}


# def get_user(db, name: str):
#     if name in db:
#         user_dict = db[name]
#         return User(**user_dict)


