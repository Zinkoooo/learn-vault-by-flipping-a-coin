import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import database_settings

logging.basicConfig()

SQLALCHEMY_DATABASE_URL = f"postgresql://{database_settings.username}:{database_settings.password}@{database_settings.hostname}/{database_settings.database}"
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARN)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
