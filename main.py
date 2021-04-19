from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashlib import sha512
from datetime import date, timedelta
from typing import Optional


class User(BaseModel):
    _ID = 1

    def __init__(self):
        self.id = User._ID
        User._ID += 1
        name: str
        surname: str
        register_date: date.today()
        vaccination_date: date

    # __next = 1  # note the underscore, tell other classes to ignore this
    # id: int = __next
    # name: str
    # surname: str
    # register_date: date
    # vaccination_date: date

    def save(self):
        self.__next += 1


app = FastAPI()
app.counter = 1


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.api_route("/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def define_method(request: Request) -> JSONResponse:
    """
    Method to return request method.
    : param: request
    : return: request method
    """
    if request.method == "POST":
        return JSONResponse({"method": request.method}, status_code=201)
    return JSONResponse({"method": request.method})


@app.get("/auth")
def authorisation(response: Response, password: str = "", password_hash: str = ""):
    """
    Method to validate hashed password
    : param: password, password_hash
    : return: HTTP 204 if password hashed by sha512 == password_hash
    """
    if password == "" or password_hash == "" or password is None or password_hash is None:
        response.status_code = 401
        return
    hashed = sha512(password.encode()).hexdigest()
    if hashed != password_hash:
        response.status_code = 401
    else:
        response.status_code = 204


