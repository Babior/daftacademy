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


@app.get("/categories", status_code=200)
async def root():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID;").fetchall()
    return {"categories": data}


@app.get("/customers")
async def customers():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT CustomerId, CompanyName, Address, PostalCode, City, Country FROM customers").fetchall()
    refactored = []
    for row in data:
        keys = ['Address', 'PostalCode', 'City', 'Country']
        full_address = []
        for key in keys:
            if row[key]:
                full_address.append(row[key])

        refactored.append(
            {'id': row['CustomerId'],
             'name': row['CompanyName'],
             'full_address': ' '.join(full_address)}
        )
    return {
        'customers': refactored
    }
