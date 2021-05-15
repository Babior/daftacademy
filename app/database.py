import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL, sslmode='require')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=conn)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
