import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

engine = create_engine('postgres://nwtxaahetowokv:7d1f3b103b6c9047a047ac557035affdd5fb71fe6e26c18155597c7cc05bc811@ec2-54-72-155-238.eu-west-1.compute.amazonaws.com:5432/dab061v57j8i6l')
conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
