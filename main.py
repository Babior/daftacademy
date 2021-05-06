import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.responses import Response

app = FastAPI()


class Category(BaseModel):
    category_name: str


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


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
@app.get("/employees", status_code=200)
async def employees(limit: int, offset: int, order: str):
    order_by = ['FirstName', 'LastNAME', 'City']
    if order not in order_by:
        raise HTTPException(status_code=400, detail='Wrong order parameter')
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY:order LIMIT:limit OFFSET :offset",
        {'limit': limit, 'offset': offset, 'order': order}).fetchall()
    return Response({"employees": [
        {"id": x['EmployeeID'], "last_name": x['LastName'], "first_name": x['FirstName'], "city": x['City']} for x in
        data]}, status_code=200)


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
    ''',{"id": id}).fetchall()
    if data is None or len(data) == 0:
        return Response(status_code=404)
    return {"orders": [
        {"id": x['OrderID'], "customer": x["CompanyName"], "quantity": x['Quantity'], "total_price": x['TotalPrice']}
        for x in data]}


# Task 4.6
@app.post("/categories", status_code=200)
async def order_by_product(category: Category):
    cursor = app.db_connection.execute(
        f"INSERT INTO Categories (CategoryName) VALUES ('{category.category_name}')"
    )
    app.db_connection.commit()
    return {
        "id": cursor.lastrowid,
        "name": category.category_name
    }

