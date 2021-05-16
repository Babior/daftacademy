from sqlalchemy import update
from sqlalchemy.orm import Session

from . import models, schemas


def get_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()


def get_supplier(db: Session, supplier_id: int):
    return db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()


def get_prod_sup(db: Session, supplier_id: int):
    return db.query(models.Product).filter(models.Product.supplier_id == supplier_id). \
        order_by(models.Product.product_id.desc()).all()


def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    supplier_id = db.query(models.Supplier).count() + 1
    db_supplier = models.Supplier(
        SupplierID=supplier_id,
        CompanyName=supplier.CompanyName,
        ContactName=supplier.ContactName,
        ContactTitle=supplier.ContactTitle,
        Address=supplier.Address,
        City=supplier.City,
        PostalCode=supplier.PostalCode,
        Country=supplier.Country,
        Phone=supplier.Phone
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier
    pass


def delete_supplier(db: Session, supplier_id: int):
    db.delete(get_supplier(db, supplier_id))
    db.commit()
    return


def update_supplier(db: Session, supplier_id: int, supplier_update: schemas.SupplierUpdate):
    update_attributes = {key: value for key, value in supplier_update.dict(exclude={'supplier_id'}).items()
                         if value is not None}
    if update_attributes != {}:
        db.execute(update(models.Supplier).where(models.Supplier.SupplierID == supplier_id).
                   values(**update_attributes))
        db.commit()

    return get_supplier(db, supplier_id=supplier_id)
