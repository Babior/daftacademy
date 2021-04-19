from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hashlib
from datetime import date, timedelta
from utils import count_letters, is_not_blank


class User(BaseModel):
    _ID = 1
    def __init__(self):
        self.id = User._ID
        User._ID += 1
        name: str
        surname: str
        register_date: date
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
def return_method(request: Request) -> JSONResponse:
    """
    Method to return request method.
    : param: request
    : return: request method
    """
    if request.method == "POST":
        return JSONResponse({"method": request.method}, status_code=201)
    return JSONResponse({"method": request.method})


@app.get("/auth", summary="Auth endpoint", status_code=401)
def auth(password: str = "", password_hash: str = ""):
    hashed_password = hashlib.sha512(password.encode("utf-8")).hexdigest()
    if is_not_blank(password) and hashed_password == password_hash:
        return Response(status_code=204)
    return Response(status_code=401)


@app.post("/register", status_code=201)
def registration(user: User):
    user.vaccination_date = user.register_date + timedelta(len(user.name) + len(user.surname))
    user.save()
    return {"id": user.id, "name": user.name, "surname": user.surname, "register_date": user.register_date,
            "vaccination_date": user.vaccination_date}
