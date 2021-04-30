import secrets
import jose
from typing import Dict, Optional

from fastapi import FastAPI, Response, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from datetime import date, datetime

from fastapi.security import HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def is_logged(session: str = Depends(app.cookie_sec), silent: bool = False):
    try:
        payload = jose.jwt.decode(session, app.secret_key)
        return payload.get("magic_key")
    except Exception:
        pass

    if silent:
        return False

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def authenticate(credentials: Optional[HTTPBasicCredentials] = Depends(app.security)):
    if not credentials:
        return False

    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_username and correct_password):
        return False
    return True


# Task 3.1
@app.get("/hello", response_class=HTMLResponse)
def hello(request: Request):
    return templates.TemplateResponse("zad3_1.html.j2", {
        "request": request, "date": datetime.date.today().isoformat()})


# Task 3.2
@app.post("/login")
def login_basic(auth: bool = Depends(authenticate)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

    response = RedirectResponse(url="/welcome")
    token = jose.jwt.encode({"magic_key": True}, app.secret_key)
    response.set_cookie("session", token)
    return response


@app.post("/login_session")
def login_session():
    return


@app.post("/login_token")
def login_token():
    return
