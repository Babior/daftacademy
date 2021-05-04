from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
import datetime
from pydantic import BaseModel
from hashlib import sha256
import secrets
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
random.seed(datetime.datetime.now())

app.stored_login_session = []
app.stored_login_token = []


# zad. 3.1

@app.get("/hello")
def print_date(request: Request, response: Response):
    return_date = date.today()
    # response.headers["content-type"] = "text/html"
    return templates.TemplateResponse("hello.html", {"request": request, "date": return_date})


# zad. 3.2

@app.get("/login_session", status_code=201)
@app.post("/login_session", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401)

    session_token = sha256(
        f"{credentials.username}{credentials.password}{str(random.randint(0, 12345))}".encode()).hexdigest()
    # session_token = "A" # tymczasowy token
    response.set_cookie(key="session_token", value=session_token)  # ustawianie cookie
    app.stored_login_session.append(session_token)  # dodawanie session token

    if len(app.stored_login_session) > 3:
        app.stored_login_session.pop(0)


@app.get("/login_token", status_code=201)
@app.post("/login_token", status_code=201)
def login_token(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401)

    session_token = sha256(
        f"{credentials.username}{credentials.password}{str(random.randint(0, 12345))}".encode()).hexdigest()
    # session_token = "AA" # tymczasowy token
    app.stored_login_token.append(session_token)  # dodawanie login token

    if len(app.stored_login_token) > 3:
        app.stored_login_token.pop(0)

    return {"token": session_token}


# zad. 3.3

@app.get("/welcome_session", status_code=200)
def welcome_session(response: Response, session_token: str = Cookie(None), format: str = ""):
    if (session_token not in app.stored_login_session) or (session_token == ""):
        raise HTTPException(status_code=401, detail="Unathorised")

    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")


@app.get("/welcome_token", status_code=200)
def welcome_token(response: Response, token: str, format: str = ""):
    if (token not in app.stored_login_token) or (token == ""):
        raise HTTPException(status_code=401, detail="Unathorised")

    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")


# zad. 3.4 // 3.5

@app.get("/logout_session")
@app.delete("/logout_session")
def logout_session(session_token: str = Cookie(None), format: str = ""):
    if (session_token not in app.stored_login_session) and (session_token not in app.stored_login_token):
        raise HTTPException(status_code=401, detail="Unathorised")

    if session_token in app.stored_login_session:
        app.stored_login_session.remove(session_token)
    else:
        app.stored_login_token.remove(session_token)

    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)


@app.get("/logout_token")
@app.delete("/logout_token")
def logout_token(token: str, format: str = ""):
    if ((token not in app.stored_login_token) and (token not in app.stored_login_session)) or (token == ""):
        raise HTTPException(status_code=401, detail="Unathorised")

    if token in app.stored_login_token:
        app.stored_login_token.remove(token)
    else:
        app.stored_login_session.remove(token)

    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)


@app.get("/logged_out", status_code=200)
def logged_out(format: str = ""):
    if format == 'json':
        return {"message": "Logged out!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Logged out!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Logged out!", status_code=200)