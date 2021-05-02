import base64
import hashlib
import random

from datetime import date, timedelta
from typing import Dict
from pydantic import BaseModel

from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import HTMLResponse


class UserIn(BaseModel):
    name: str
    surname: str


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    register_date: date
    vaccination_date: date


app = FastAPI()
app.counter: int = 1
app.users: Dict[int, UserOut] = {}
app.session_token = []
app.token = []


# Task 1.1
@app.get("/")
def root():
    return {"message": "Hello world!"}


# Task 1.2
@app.api_route("/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def define_method(request: Request) -> JSONResponse:
    """
    Method to return request method.
    : param: request
    : return: JSON response with request method
    """
    if request.method == "POST":
        return JSONResponse({"method": request.method}, status_code=201)
    return JSONResponse({"method": request.method})


# Task 1.3
@app.get("/auth")
def authorisation(password: str = "", password_hash: str = ""):
    """
    Method to validate hashed password.
    : param: password, password_hash
    : return: response HTTP 204 if password hashed by sha512 == password_hash
    """
    if password is not None and password_hash is not None and password != "" and password_hash != "":
        return Response(status_code=401)
    hashed = hashlib.sha512(password.encode()).hexdigest()
    if hashed == password_hash:
        return Response(status_code=204)
    return Response(status_code=401)


# Task 1.4
@app.post("/register", response_model=UserOut, status_code=201)
def registration(user: UserIn):
    """
    Method to add users to fake db.
    param: user's name and surname
    return: user object with id, name, surname, registration date and
    vaccination date(=registration date + sum of letter in name and surname) HTTP 204 if
    """
    user_id = app.counter
    register_date = date.today()
    vaccination_date = register_date + timedelta(
        (sum(map(str.isalpha, user.name)) + sum(map(str.isalpha, user.surname))))
    user_out = UserOut(
        id=user_id,
        name=user.name,
        surname=user.surname,
        register_date=register_date,
        vaccination_date=vaccination_date,
    )
    app.users[app.counter] = user_out
    app.counter += 1
    return user_out


# Task 1.5
@app.get('/patient/{id}', status_code=404, response_model=UserOut)
def get_patient(user_id: int):
    """
    Method to return users by id.
    param: user's id
    return: user object with id, name, surname, registration date and vaccination date
    """
    if user_id < 1:
        return Response(status_code=400, detail="Invalid patient id")

    if user_id not in app.users:
        return Response(status_code=404, detail="Patient not found")

    return app.users.get(user_id)


