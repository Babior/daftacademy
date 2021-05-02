import base64
import hashlib
import random
import secrets

from datetime import date, timedelta
from typing import Dict
from pydantic import BaseModel

from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import HTMLResponse

from typing import Dict, Optional

from fastapi import Depends, FastAPI, Response, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie, HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import RedirectResponse


class Patient(BaseModel):
    name: str
    surname: str


class DaftAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter: int = 0
        self.storage: Dict[int, Patient] = {}
        self.security = HTTPBasic(auto_error=False)
        self.secret_key = "kluczyk"
        self.API_KEY = "session"
        self.cookie_sec = APIKeyCookie(name=self.API_KEY, auto_error=False)
        self.templates = Jinja2Templates(directory="templates")


app = DaftAPI()


# Task3.1
@app.get("/hello")
async def hello():
    today_date = date.today().isoformat()
    content = "<h1>Hello! Today date is {}</h1>".format(today_date)
    return HTMLResponse(content=content)


# Task3.2
def check_password_and_generate_token(header):
    auth_header = header
    decoded_data = auth_header.split(" ")[1]
    decoded_data_bytes = decoded_data.encode('ascii')
    base_decode_result = base64.b64decode(decoded_data_bytes)
    result = base_decode_result.decode('ascii')
    user, password = tuple(result.split(":"))
    if user == "4dm1n" and password == "NotSoSecurePa$$":
        random_num = random.randint(0, 1000)
        token = hashlib.sha512((user + password + str(random_num)).encode())
        return token.hexdigest()
    return False


@app.post("/login_session")
async def login_session(response: Response, Authorization: str = Header(None)):
    token = check_password_and_generate_token(Authorization)
    if token:
        if len(app.session_token) == 3:
            app.session_token = app.session_token[1:]
        app.session_token.append(token)
        response.set_cookie(key="session_token", value=token)
        response.status_code = 201
        return "OK"
    raise HTTPException(status_code=401, detail='Unauthorized')


@app.post("/login_token")
async def login_token(response: Response, Authorization: str = Header(None)):
    token = check_password_and_generate_token(Authorization)
    if token:
        if len(app.token) == 3:
            app.token = app.token[1:]
        app.token.append(token)
        response.status_code = 201
        return {"token": token}
    raise HTTPException(status_code=401, detail='Unauthorized')