import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs.config import settings

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://daeha:difwkrka1201@127.0.0.1/test"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_ID}:{settings.DB_PW}@{settings.DB_ADDRESS}/{settings.DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextlib.contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
