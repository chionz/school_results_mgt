import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
print(DATABASE_URL)

#engine = create_engine(DATABASE_URL)

metadata = MetaData()
Base = declarative_base()


def get_db_engine(test_mode: bool = False):
    DATABASE_URL = os.getenv("DB_URL")

    if os.getenv("DB_TYPE") == "sqlite" or test_mode:
        BASE_PATH = f"sqlite:///{BASE_DIR}"
        DATABASE_URL = BASE_PATH + "/"

        if test_mode:
            DATABASE_URL = BASE_PATH + "test.db"

            return create_engine(
                DATABASE_URL, connect_args={"check_same_thread": False}
            )
    elif os.getenv("DB_TYPE") == "postgresql":
        DATABASE_URL = DATABASE_URL = os.getenv("DB_URL")
        
    #print (f"connecting to {DATABASE_URL}")
    return create_engine(DATABASE_URL)


engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)


import app.models

def create_database():
    
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()