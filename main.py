from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashlib import sha512
from datetime import date, timedelta
from typing import Optional
from utils import count_letters, is_not_blank


class UserIn(BaseModel):
    name: str
    surname: str


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    register_date: date
    vaccination_date: date


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


@app.post("/register", response_model=UserOut, status_code=201)
def register(user: UserIn):
    user_id = app.user_id
    app.user_id += 1
    register_date = date.today()
    len_name_surname = count_letters(user.name) + count_letters(user.surname)
    vaccination_date = register_date + timedelta(len_name_surname)
    user_out = UserOut(
        id=user_id,
        name=user.name,
        surname=user.surname,
        register_date=register_date,
        vaccination_date=vaccination_date,
    )
    app.users[user_id] = user_out
    return user_out


# @app.post("/register", response_model=Patient)
# def register_post(person: Person, response: Response):
#     len_name = len(''.join([i for i in person.name if i.isalpha()]))
#     len_surname = len(''.join([i for i in person.surname if i.isalpha()]))
#     len_sum = len_name + len_surname
#     response_date = datetime.date.today()
#     date_to_add = datetime.timedelta(days=len_sum)
#     vaccination_date = response_date + date_to_add
#     person_id = len(app.list_of_patients) + 1
#     response.status_code = 201
#     patient = Patient(id=person_id, name=person.name, surname=person.surname,
#                       register_date=response_date.isoformat(), vaccination_date=vaccination_date.isoformat())
#     app.list_of_patients.append(patient)
#     return patient
