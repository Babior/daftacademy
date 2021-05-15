import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("postgresql://postgres:DaftAcademy@127.0.0.1:5432/northwind")

engine = create_engine("postgresql://postgres:DaftAcademy@127.0.0.1:5432/northwind")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()