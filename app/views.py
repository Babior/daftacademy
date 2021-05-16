from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import PositiveInt
from sqlalchemy.orm import Session

from . import crud, schemas, models
from .database import get_db

router = APIRouter()


# Task 5.1
@router.get("/suppliers", response_model=List[schemas.Supplier])
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)


@router.get("/suppliers/{supplier_id}", response_model=schemas.SupplierBase)
async def get_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


# Task 5.2
@router.get("/suppliers/{supplier_id}/products")
async def get_suppliers_products(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db_suppliers_products = crud.get_prod_sup(db, supplier_id)
    return [{
        "ProductID": product.ProductID,
        "ProductName": product.ProductName,
        "Category": {
            "CategoryID": product.CategoryID,
            "CategoryName": product.CategoryName,
        },
        "Discontinued": product.Discontinued,
    } for product in db_suppliers_products]


# Task 5.3
@router.post("/suppliers", response_model=schemas.SupplierBase, status_code=201)
async def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    return crud.create_supplier(db=db, supplier=supplier)


# Task 5.4
@router.put("/suppliers/{supplier_id}", response_model=schemas.SupplierBase, status_code=200)
async def create_supplier(supplier_id: PositiveInt, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=401, detail="Supplier not found")
    crud.update_supplier(db, supplier_id, supplier)
    return crud.get_supplier(db, supplier_id)


# Task 5.5
@router.delete("/suppliers/{supplier_id}", status_code=204)
async def delete_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=401, detail="Supplier not found")
    return crud.delete_supplier(db=db, supplier_id=supplier_id)


