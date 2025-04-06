# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Supabase connection string format
# The format is postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:meghendralord@db.nbvwwbvarqitzeimgwfy.supabase.co:5432/postgres"

# You may need to add connection pool settings depending on your requirements
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()