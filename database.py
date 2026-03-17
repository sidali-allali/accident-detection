from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# تكوين قاعدة البيانات
DATABASE_URL = "sqlite:///./accidents.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # ضروري لـ SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# مدير السياق لجلسات قاعدة البيانات
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()