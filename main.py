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


@app.get("/")
def root():
    return {"message": "Hello world!"}


# Task 3.1
@app.get("/hello", response_class=HTMLResponse)
def hello(request: Request):
    return templates.TemplateResponse("zad3_1.html.j2", {
        "request": request, "date": datetime.date.today().isoformat()})



