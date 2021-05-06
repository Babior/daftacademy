import sqlite3

from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


@app.get("/data")
async def root():
    cursor = app.db_connection.execute("SELECT ProductName FROM Products")
    data = cursor.fetchall()
    return {"data": data}


@app.get("/categories", status_code=200)
async def root():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID;").fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x["CategoryName"]} for x in data]}


@app.get("/customers", status_code=200)
async def root():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country FROM Customers;").fetchall()
    return {"customers": [{"id": x["CustomerID"], "name": x["CompanyName"],
                           "full_address": f"{x['Address']} {x['PostalCode']} {x['City']} {x['Country']}"} for x in
                          data]}

