import secrets
import sqlite3
import uuid

from contextlib import contextmanager
from datetime import datetime
from hashlib import sha512
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status, Query
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
app.username = "4dm1n"
app.password = "NotSoSecurePa$$"
app.secret_key = "T00Sh0rtAppS3cretK3y"
app.api_token: List[str] = []
app.session_token: List[str] = []
app.token_limits = 3

app = FastAPI()


class Category(BaseModel):
    name: str


def add_token(token: str, cache_ns: str):
    tokens = getattr(app, cache_ns)
    if len(tokens) >= app.token_limits:
        tokens.pop(0)
    tokens.append(token)
    setattr(app, cache_ns, tokens)


def remove_token(token: str, cache_ns: str):
    tokens = getattr(app, cache_ns)
    try:
        index = tokens.index(token)
        tokens.pop(index)
        setattr(app, cache_ns, tokens)
    except ValueError:
        return None


def generate_token(request: Request):
    return sha512(
        bytes(
            f"{uuid.uuid4().hex}{app.secret_key}{request.headers['authorization']}",
            "utf-8",
        )
    ).hexdigest()


def auth_basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    correct_user = secrets.compare_digest(credentials.username, app.username)
    correct_pass = secrets.compare_digest(credentials.password, app.password)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
        )

    return True


def auth_session(session_token: str = Cookie(None)):
    if app.session_token and session_token in app.session_token:
        return session_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
    )


def auth_token(token: Optional[str] = None):
    if app.api_token and token in app.api_token:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
    )


@contextmanager
def response_class(format: str):
    resp_cls = PlainTextResponse
    if format == "json":
        resp_cls = JSONResponse
    if format == "html":
        resp_cls = HTMLResponse

    yield resp_cls


@contextmanager
def response_welcome_msg(format: str):
    resp_msg = "Welcome!"
    if format == "json":
        resp_msg = {"message": "Welcome!"}
    if format == "html":
        resp_msg = "<h1>Welcome!</h1>"

    yield resp_msg


# Task 3.1
@app.get("/hello", response_class=HTMLResponse, tags=['Lesson 3'])
def read_root_hello():
    return f"""
    <html>
        <head>
            <title></title>
        </head>
        <body>
            <h1>Hello! Today date is {datetime.now().date()}</h1>
        </body>
    </html>
    """


# Task 3.2
@app.post("/login_session", status_code=201, response_class=HTMLResponse, tags=['Lesson 3'])
def create_session(
        request: Request, response: Response, auth: bool = Depends(auth_basic_auth)
):
    token = generate_token(request)
    add_token(token, "session_token")
    response.set_cookie(key="session_token", value=token)
    return ""


@app.post("/login_token", status_code=201, tags=['Lesson 3'])
def create_token(request: Request, auth: bool = Depends(auth_basic_auth)):
    token = generate_token(request)
    add_token(token, "api_token")
    return {"token": token}


# Task 3.3
@app.get("/welcome_session", tags=['Lesson 3'])
def show_welcome_session(received_token: str = Depends(auth_session), format: str = ""):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/welcome_token", tags=['Lesson 3'])
def show_welcome_token(received_token: str = Depends(auth_token), format: str = "", tags=['Lesson 3']):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/logged_out", tags=['Lesson 3'])
def logged_out(format: str = ""):
    with response_class(format) as resp_cls:
        if format == "json":
            return resp_cls(content={"message": "Logged out!"})
        if format == "html":
            return resp_cls(content="<h1>Logged out!</h1>")

        return resp_cls(content="Logged out!")


# Task 3.4
@app.delete("/logout_session", tags=['Lesson 3'])
def logout_session(received_token: str = Depends(auth_session), format: str = ""):
    remove_token(received_token, "session_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


@app.delete("/logout_token", tags=['Lesson 3'])
def logout_token(received_token: str = Depends(auth_token), format: str = ""):
    remove_token(received_token, "api_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


# Lesson 4
@app.on_event("startup", )
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


# Task 4.1
@app.get("/categories", status_code=200, tags=['Lesson 4'])
async def all_categories():
    app.db_connection.row_factory = sqlite3.Row
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID;").fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x["CategoryName"]} for x in categories]}


@app.get("/customers", status_code=200, tags=['Lesson 4'])
async def all_customers():
    app.db_connection.row_factory = sqlite3.Row
    customers = app.db_connection.execute(
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country FROM Customers;").fetchall()
    modified = []
    for tuple in customers:
        keys = [tuple['Address'], tuple['PostalCode'], tuple['City'], tuple['Country']]
        full_address = str
        if None in keys:
            modified.append(
                {'id': tuple['CustomerID'],
                 'name': tuple['CompanyName'],
                 'full_address': None}
            )
        else:
            modified.append(
                {'id': tuple['CustomerID'],
                 'name': tuple['CompanyName'],
                 'full_address': f"{tuple['Address']} {tuple['PostalCode']} {tuple['City']} {tuple['Country']}"}
            )

    return {"customers": modified}


# Task 4.2
@app.get("/products/{id}", status_code=200, tags=['Lesson 4'])
async def single_product(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = ?", (id,)).fetchone()
    if data is None:
        return Response(status_code=404)
    return {"id": data['ProductID'], "name": data['ProductName']}


# Task 4.3
@app.get('/employees', tags=['Lesson 4'])
async def employees(limit: int = 0, offset: int = 0, order: str = '') -> Dict:
    order_dict = {'first_name': 'FirstName', 'last_name': 'LastName', 'city': 'City'}
    try:
        if offset < 0 or limit < 0 or (offset and not limit):
            raise ValueError()
        if order:
            if order not in order_dict:
                raise ValueError()
        else:
            order = 'default'
            order_dict['default'] = 'EmployeeID'

        query = f'''SELECT EmployeeID id, LastName last_name, FirstName first_name, City city
        FROM EMPLOYEES
        ORDER BY {order_dict[order]}
        {f"LIMIT {limit}" if limit > 0 else ""}
        {f"OFFSET {offset}" if offset > 0 else ""}'''

        app.db_connection.row_factory = sqlite3.Row
        data = app.db_connection.execute(query).fetchall()
        return {'employees': data}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Bad Request, check query parameters")


# Task 4.4
@app.get("/products_extended", status_code=200, tags=['Lesson 4'])
async def prod_extended():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
        SELECT ProductID, ProductName, CategoryName, CompanyName 
        FROM Products INNER JOIN Categories 
        ON Products.CategoryID = Categories .CategoryID 
        INNER JOIN Suppliers 
        ON Products.SupplierID = Suppliers.SupplierID;
        ''').fetchall()
    return {"products_extended": [
        {"id": x['ProductID'], "name": x["ProductName"], "category": x['CategoryName'], "supplier": x['CompanyName']}
        for x in data]}


# Task 4.5
@app.get("/products/{id}/orders", status_code=200, tags=['Lesson 4'])
async def order_by_product(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
    SELECT Orders.OrderID, Customers.CompanyName, od.Quantity, ROUND((od.UnitPrice * od.Quantity) - (od.Discount * (od.UnitPrice * od.Quantity)), 2) AS TotalPrice
    FROM Orders INNER JOIN Customers
    ON Orders.CustomerID = Customers.CustomerID
    INNER JOIN "Order Details" od
    ON Orders.OrderID = od.OrderID
    WHERE od.ProductID = (SELECT Products.ProductID FROM Products WHERE Products.ProductID = :id);
    ''', {"id": id}).fetchall()
    if data is None or len(data) == 0:
        return Response(status_code=404)
    return {"orders": [
        {"id": x['OrderID'], "customer": x["CompanyName"], "quantity": x['Quantity'], "total_price": x['TotalPrice']}
        for x in data]}


# Task 4.6
@app.post('/categories', tags=['Lesson 4'])
async def categories(category: Category):
    cursor = app.db_connection.execute(
        f"INSERT INTO Categories (CategoryName) VALUES ('{category.name}')"
    )
    app.db_connection.commit()
    return JSONResponse({"id": cursor.lastrowid, "name": category.name}, status_code=status.HTTP_201_CREATED)


@app.put('/categories/{category_id}', tags=['Lesson 4'])
async def categories(category: Category, category_id: int):
    cursor = app.db_connection.cursor()
    data = cursor.execute('''
        SELECT CategoryID FROM Categories WHERE CategoryID = :category_id
    ''', {'category_id': category_id}).fetchone()

    if not data:
        raise HTTPException(404, f"Category id: {category_id} Not Found")
    cursor = app.db_connection.cursor()
    cursor.execute('''
            UPDATE Categories SET CategoryName = :name WHERE CategoryID = :category_id
        ''', {'category_id': category_id, 'name': category.name})
    app.db_connection.commit()
    return {'id': category_id, 'name': category.name}


@app.delete('/categories/{category_id}', tags=['Lesson 4'])
async def categories(category_id: int):
    cursor = app.db_connection.cursor()
    data = cursor.execute('''
        SELECT CategoryID FROM Categories WHERE CategoryID = :category_id
    ''', {'category_id': category_id}).fetchone()

    if not data:
        raise HTTPException(404, f"Category id: {category_id} Not Found")
    cursor = app.db_connection.cursor()
    cursor.execute('''
            DELETE FROM Categories WHERE CategoryID = :category_id
        ''', {'category_id': category_id}).fetchone()
    app.db_connection.commit()
    return {'deleted': 1}