from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashlib import sha512
from datetime import date, timedelta
from typing import Optional


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
app.users = []


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
def authorisation(password: str, password_hash: str, response: Response):
    """
    Method to validate hashed password
    : param: password, password_hash
    : return: HTTP 204 if password hashed by sha512 == password_hash
    """
    if (password != None) and (password_hash != None) and (password != "") and (password_hash != ""):
        response.status_code = 401
        return
    hashed = sha512(password.encode()).hexdigest()
    if hashed != password_hash:
        response.status_code = 401
    else:
        response.status_code = 204


@app.post("/register", response_model=UserOut, status_code=201)
def registration(user: UserIn):
    """
    Method to add users to fake db : param: user's name and surname :
    return: user object with id, name, surname, registration date and
    vaccination date(=registration date + sum of letter in name and surname) HTTP 204 if
    """
    user_id = len(app.users) + 1
    register_date = date.today()
    vaccination_date = register_date + timedelta(days=(sum(map(str.isalpha, user.name)) + sum(map(str.isalpha, user.surname))))
    # vaccination_date = register_date + timedelta(len(user.name) + len(user.surname))
    print(len(user.name) + len(user.surname))
    user_out = UserOut(
        id=user_id,
        name=user.name,
        surname=user.surname,
        register_date=register_date,
        vaccination_date=vaccination_date,
    )
    app.users.append(user_out)
    return user_out


@app.get("/patient/{id}", response_model=UserOut)
async def patient_get(id: int, response: Response):
    if id < 1:
        response.status_code = 400
    elif id > len(app.users):
        response.status_code = 404
    else:
        response.status_code = 200
        return app.users[id-1]