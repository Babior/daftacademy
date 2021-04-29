from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from datetime import date, datetime
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/hello", response_class=HTMLResponse)
def hello_func(request: Request):
    return templates.TemplateResponse("zad3_1.html.j2", {
        "request": request, "date": datetime.today().strftime('%Y-%m-%d')})
