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


def is_logged(session: str = Depends(app.cookie_sec)):
    try:
        payload = jwt.decode(session, app.secret_key)
        return payload.get("magic_key")
    except Exception:
        pass

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def authenticate(credentials: Optional[HTTPBasicCredentials] = Depends(app.security)):
    if not credentials:
        return False

    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_username and correct_password):
        return False
    return True


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
    # if user == "4dm1n" and password == "NotSoSecurePa$$":
    # random_num = random.randint(0, 1000)
    # token = hashlib.sha512((user + password + str(random_num)).encode())
    if authenticate():
        return hashlib.sha256(f"{user}{password}{app.secret_key}".encode()).hexdigest()
    return False


@app.post("/login_session")
async def login_basic(auth: bool = Depends(authenticate)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

    response = RedirectResponse(url="/welcome")
    session_token = jwt.encode({"magic_key": True}, app.secret_key)
    if len(app.session_cookie_tokens) >= 3:
        del app.session_cookie_tokens[0]
    app.session_cookie_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.post("/login_token", status_code=201)
def login_token(auth: bool = Depends(authenticate)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

    token_value = jwt.encode({"magic_key": True}, app.secret_key)
    if len(app.session_cookie_tokens) >= 3:
        del app.session_cookie_tokens[0]
    app.session_tokens.append(token_value)
    return {"token": token_value}


# Task 3.3
@app.get("/welcome_session")
def welcome(session_token: str = Cookie(None), is_format: Message = Depends(Message),
            is_logged: bool = Depends(is_logged)):
    if not session_token or session_token not in app.session_cookie_tokens:
        raise HTTPException(status_code=401, detail="Unauthorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()


@app.get("/welcome_token")
def welcome_token(token: Optional[str] = Query(None), is_format: Message = Depends(Message),
                  is_logged: bool = Depends(is_logged)):
    if not token or token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    else:
        is_format.word = "Welcome"
        return is_format.return_message()
