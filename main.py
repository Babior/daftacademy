import base64
import hashlib
import secrets
import jwt

from datetime import date
from typing import Dict

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi import FastAPI, Request, Response, Header, HTTPException, Query, Cookie
from starlette.responses import HTMLResponse, PlainTextResponse, JSONResponse

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


def set_response_based_on_format(format: str) -> Response:
    sc = status.HTTP_200_OK
    responses = {'json': JSONResponse({"message": "Welcome!"}, status_code=sc),
                 'html': HTMLResponse('<h1>Welcome!</h1>', status_code=sc)}
    return responses[format] if format in responses else PlainTextResponse('Welcome!', status_code=sc)


def set_response_based_on_format(format: str) -> Response:
    sc = status.HTTP_200_OK
    responses = {'json': JSONResponse({"message": "Welcome!"}, status_code=sc),
                 'html': HTMLResponse('<h1>Welcome!</h1>', status_code=sc)}
    return responses[format] if format in responses else PlainTextResponse('Welcome!', status_code=sc)


@app.get('/welcome_session')
async def welcome_session(request: Request, format: str = ''):
    try:
        if not request.cookies.get('session_token'):
            raise KeyError
        return set_response_based_on_format(format)
    except KeyError:
        return PlainTextResponse('Welcome!', status_code=status.HTTP_401_UNAUTHORIZED)


@app.get('/welcome_token')
async def welcome_token(request: Request, token: str = '', format: str = ''):
    try:
        if request.cookies.get('token') != token:
            raise KeyError
        return set_response_based_on_format(format)
    except KeyError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)





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
async def logout_session(format: str = Query(None), session_token=Cookie(None)):
    if session_token is False or session_token not in app.session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    app.session_token.remove(session_token)
    resp = RedirectResponse("/logged_out?format={}".format(format), status_code=302)
    return resp


@app.delete("/logout_token")
async def logout_token(format: str = Query(None), token: str = Query(None)):
    if token is False or token not in app.token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    app.token.remove(token)
    resp = RedirectResponse("/logged_out?format={}".format(format), status_code=302)
    return resp


@app.get("/logged_out")
async def logged_out(format: str = Query(None)):
    if format == "json":
        msg = {"message": "Logged out!"}
        json_msg = jsonable_encoder(msg)
        return JSONResponse(json_msg)
    elif format == "html":
        msg = "<h1>Logged out!</h1>"
        return HTMLResponse(content=msg)
    else:
        return PlainTextResponse(content="Logged out!")
