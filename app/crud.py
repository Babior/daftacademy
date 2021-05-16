from sqlalchemy.orm import Session

from . import models, schemas


def get_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()


def get_supplier(db: Session, supplier_id: int):
    return db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()


def get_prod_sup(db: Session, supplier_id: int):
    return db.query(models.Product.ProductID,
                    models.Product.ProductName,
                    models.Category.CategoryID,
                    models.Category.CategoryName,
                    models.Product.Discontinued,
                    ).join(models.Supplier, models.Product.SupplierID == models.Supplier.SupplierID) \
        .join(models.Category, models.Product.CategoryID == models.Category.CategoryID) \
        .filter(models.Product.SupplierID == supplier_id) \
        .order_by(models.Product.ProductID.desc()).all()


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
    # db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).delete()
    db.commit()
    return


def update_supplier(db: Session, supplier_id: int, supplier: schemas.SupplierUpdate):
    updated_supplier = {col: val for col, val in dict(supplier).items() if val is not None}
    if updated_supplier:
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).update(values=updated_supplier)
        db.commit()
        pass
