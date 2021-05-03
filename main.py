import base64
import hashlib
import secrets
import jwt

from datetime import date
from typing import Dict
from pydantic import BaseModel

from fastapi import FastAPI, Request, Response, Header, HTTPException, Query, Cookie
from starlette.responses import HTMLResponse, PlainTextResponse

from typing import Dict, Optional

from fastapi import Depends, FastAPI, Response, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie, HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import RedirectResponse


class Patient(BaseModel):
    name: str
    surname: str


class Message:
    def __init__(self, format: Optional[str] = Query("")):
        self.format = format
        self.word = ""

    def return_message(self):
        """ Return message in correct format (json/html/plain) """
        if self.format == "json":
            message = {"message": f"{self.word}!"}
        elif self.format == "html":
            message = HTMLResponse(f"<h1>{self.word}!</h1>", status_code=200)
        else:
            message = PlainTextResponse(f"{self.word}!", status_code=200)
        return message


class DaftAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter: int = 0
        self.storage: Dict[int, Patient] = {}
        self.security = HTTPBasic(auto_error=False)
        self.secret_key = "kluczyk"
        self.API_KEY = "session"
        self.session_cookie_tokens = []
        self.session_tokens = []
        self.cookie_sec = APIKeyCookie(name=self.API_KEY, auto_error=False)
        self.templates = Jinja2Templates(directory="templates")


app = DaftAPI()
app.counter = 0
app.session_token = []
app.token = []


def authenticate(credentials: HTTPBasicCredentials = Depends(app.security)):
    """ Helper function for username/password check """
    if not credentials:
        return False

    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_username and correct_password):
        status_code = 401
    else:
        status_code = 200
    return {"status_code": status_code,
            "valid_username": correct_username,
            "valid_password": correct_password}


# Task 3.1
@app.get("/hello")
async def hello():
    today_date = date.today().isoformat()
    content = "<h1>Hello! Today date is {}</h1>".format(today_date)
    return HTMLResponse(content=content)


# Task 3.2
@app.post("/login_session", status_code=201)
def login_session(response: Response, auth: dict = Depends(authenticate)):
    if auth["status_code"] == 200:
        secret_key = secrets.token_hex(16)
        session_token = hashlib.sha256(
            f'{auth["valid_username"]}{auth["valid_password"]}{secret_key}'.encode()).hexdigest()
        if len(app.session_cookie_tokens) >= 3:
            del app.session_cookie_tokens[0]
        app.session_cookie_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
    elif auth["status_code"] == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Basic"})
    return {"message": "Session established"}


@app.post("/login_token", status_code=201)
def login_token(auth: dict = Depends(authenticate)):
    if auth["status_code"] == 200:
        secret_key = secrets.token_hex(16)
        token_value = hashlib.sha256(
            f'{auth["valid_username"]}{auth["valid_password"]}{secret_key}'.encode()).hexdigest()
        if len(app.session_tokens) >= 3:
            del app.session_tokens[0]
        app.session_tokens.append(token_value)
    elif auth["status_code"] == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Basic"})
    return {"token": token_value}


# Task 3.3
@app.get("/welcome_session")
def welcome_session(session_token: str = Cookie(None), is_format: Message = Depends(Message)):
    if not session_token or session_token not in app.session_cookie_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()


@app.get("/welcome_token")
def welcome_token(token: Optional[str] = Query(None), is_format: Message = Depends(Message)):
    if not token or token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()


# Task 3.4
@app.delete("/logout_session")
def logout_session(session_token: str = Cookie(None), format: str = Query("")):
    if not session_token or session_token not in app.session_cookie_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        app.session_cookie_tokens.remove(session_token)
        url = f"/logged_out?format={format}"
        return RedirectResponse(url=url, status_code=303)


@app.delete("/logout_token")
def logout_token(token: Optional[str] = Query(None), format: str = Query("")):
    if not token or token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        app.session_tokens.remove(token)
        url = f"/logged_out?format={format}"
        return RedirectResponse(url=url, status_code=303)


@app.get("/logged_out")
def logged_out(is_format: Message = Depends(Message)):
    is_format.word = "Logged out"
    return is_format.return_message()
