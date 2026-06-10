import os

#from dotenv import load_dotenv
from app.core.secrets_manager import get_db_secret
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from urllib.parse import quote_plus # for encoding special characters in the password when constructing the database URL

# load_dotenv()
secret = get_db_secret()

''' for RDS secret manager, we store in the secretmanager as JSON format, so we can directly load it as a dict and access the values by keys. '''
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")
DB_USER = secret["DB_USER"]
DB_PASSWORD = secret["DB_PASSWORD"]
DB_HOST = secret["DB_HOST"]
DB_PORT = secret["DB_PORT"]
DB_NAME = secret["DB_NAME"]


DATABASE_URL = ( # "mysql+pymysql://db_user:db_password@db_host/db_name"
    f"mysql+pymysql://{DB_USER}:"
    f"{quote_plus(DB_PASSWORD)}@"
    f"{DB_HOST}:"
    f"{DB_PORT}/"
    f"{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# -------------------------------------
# Dependency Injection for FastAPI
# -------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()