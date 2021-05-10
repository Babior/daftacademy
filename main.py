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
    category_name: str


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
@app.get("/hello", response_class=HTMLResponse)
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
@app.post("/login_session", status_code=201, response_class=HTMLResponse)
def create_session(
        request: Request, response: Response, auth: bool = Depends(auth_basic_auth)
):
    token = generate_token(request)
    add_token(token, "session_token")
    response.set_cookie(key="session_token", value=token)
    return ""


@app.post("/login_token", status_code=201)
def create_token(request: Request, auth: bool = Depends(auth_basic_auth)):
    token = generate_token(request)
    add_token(token, "api_token")
    return {"token": token}


# Task 3.3
@app.get("/welcome_session")
def show_welcome_session(received_token: str = Depends(auth_session), format: str = ""):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/welcome_token")
def show_welcome_token(received_token: str = Depends(auth_token), format: str = ""):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/logged_out")
def logged_out(format: str = ""):
    with response_class(format) as resp_cls:
        if format == "json":
            return resp_cls(content={"message": "Logged out!"})
        if format == "html":
            return resp_cls(content="<h1>Logged out!</h1>")

        return resp_cls(content="Logged out!")


# Task 3.4
@app.delete("/logout_session")
def logout_session(received_token: str = Depends(auth_session), format: str = ""):
    remove_token(received_token, "session_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


@app.delete("/logout_token")
def logout_token(received_token: str = Depends(auth_token), format: str = ""):
    remove_token(received_token, "api_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


# Lesson 4
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


@app.get("/", status_code=200)
async def root():
    return JSONResponse({"message": "Welcome to the club!"})


# Task 4.1
@app.get("/categories", status_code=200)
async def all_categories():
    app.db_connection.row_factory = sqlite3.Row
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID;").fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x["CategoryName"]} for x in categories]}


@app.get("/customers", status_code=200)
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
@app.get("/products/{id}", status_code=200)
async def single_product(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = ?", (id,)).fetchone()
    if data is None:
        return Response(status_code=404)
    return {"id": data['ProductID'], "name": data['ProductName']}


# Task 4.3
# @app.get("/employees", status_code=200)
# async def get_employees(limit: int, offset: int, order: str = "id"):
#     order_by = ['EmployeeID', 'FirstName', 'LastName', 'City', "id", "last_name", "first_name", "city"]
#     if order not in order_by:
#         return Response(status_code=400)
#     app.db_connection.row_factory = sqlite3.Row
#     # data = app.db_connection.execute('''
#     #             SELECT EmployeeID id, LastName last_name, FirstName first_name, City city
#     #             FROM Employees
#     #             ORDER BY:order ASC
#     #             LIMIT:limit
#     #             OFFSET :offset''',
#     #             {'limit': limit, 'offset': offset, 'order': order}).fetchall()
#     data = app.db_connection.execute('''
#                  SELECT EmployeeID id, LastName last_name, FirstName first_name, City city
#                  FROM Employees
#                  ORDER BY {order}
#                  LIMIT 5
#                  OFFSET 2''', {'order': order}).fetchall()
#     return {"employees": data}

@app.get('/employees')
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
@app.get("/products_extended", status_code=200)
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
@app.get("/products/{id}/orders", status_code=200)
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
# @app.post("/categories", status_code=201)
# async def add_category(category: Category):
#     cursor = app.db_connection.execute('''INSERT INTO Categories (CategoryName) VALUES (?)''', (category.name, ))
#     app.db_connection.commit()
#     app.db_connection.row_factory = sqlite3.Row
#     new_category_id = cursor.lastrowid
#     category = app.db_connection.execute('''SELECT CategoryID id, CategoryName name FROM Categories WHERE CategoryID = ?''', (new_category_id, )).fetchone()
#     return category
#
#
# @app.post("/categories/{id}", status_code=200)
# async def update_category(category_id: int, category: Category):
#     count = app.db_connection.execute("SELECT COUNT(*) FROM Categories").fetchone()
#     if category_id < 0 or category_id > count[0]:
#         return Response(status_code=404)
#     cursor = app.db_connection.execute(
#         "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?", (
#             category.category_name, category_id)
#     )
#     app.db_connection.commit()
#     app.db_connection.row_factory = sqlite3.Row
#     data = app.db_connection.execute(
#         """SELECT CategoryID AS id, CategoryName AS name FROM Categories WHERE CategoryID = ?""",
#         (category_id,)).fetchone()
#     return data
#
#
# @app.delete("/categories/{id}", status_code=200)
# async def delete_category(category_id: int):
#     count = app.db_connection.execute("SELECT COUNT(*) FROM Categories").fetchone()
#     if category_id < 0 or category_id > count[0]:
#         return Response(status_code=404)
#     cursor = app.db_connection.execute("DELETE FROM Categories WHERE CategoryID = ?", (category_id,))
#     app.db_connection.commit()
#     return {"deleted": cursor.rowcount}


#Hubert
@app.post("/categories")
async def add_category(category: Category, response: Response):
    cursor = app.db_connection.cursor()
    cursor.execute(
        'INSERT INTO Categories (CategoryName) VALUES (?)', (category.name, )
    )
    app.db_connection.commit()
    new_id = cursor.lastrowid
    response.status_code = 201
    return Category(id=new_id, name=category.name)


@app.put("/categories/{id}")
async def modify_category(id: int, category: Category):
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchall()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No such category")
    app.db_connection.execute(
        'UPDATE Categories SET CategoryName=:name WHERE CategoryID=:id', {"name": category.name, 'id': id}
    )
    app.db_connection.commit()
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchone()
    return Category(id=results[0], name=results[1])


@app.delete("/categories/{id}")
async def delete_category(id: int):
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchall()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No such category")
    app.db_connection.execute(
        'PRAGMA foreign_keys=off;'
    )
    app.db_connection.execute(
        'DELETE FROM Categories WHERE CategoryID=:id', {'id': id}
    )
    app.db_connection.commit()
    msg = {"deleted": 1}
    return JSONResponse(status_code=200, content=msg)
