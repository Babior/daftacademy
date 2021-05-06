import sqlite3
from http.client import HTTPException

from fastapi import FastAPI
from starlette import status
from starlette.responses import Response

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


@app.get("/categories", status_code=200)
async def root():
    app.db_connection.row_factory = sqlite3.Row
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID;").fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x["CategoryName"]} for x in categories]}


@app.get("/customers", status_code=200)
async def root():
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


@app.get("/products/{id}")
async def single_supplier(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = ?", (id,)).fetchone()
    if data is None:
        return Response(status_code=404)
    return {"id": data['ProductID'], "name": data['ProductName']}
