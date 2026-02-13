import os
from sqlmodel import SQLModel, Session, create_engine


def get_database_url():
    # TODO: Configure deployment to use environment variables
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./db.sqlite")
    return db_url


def init_db():
    """
    Creates all tables in the database using the definitions in the SQLModel metadata.
    """
    print("Initializing database...")
    db_engine = create_engine(get_database_url())
    SQLModel.metadata.create_all(db_engine)


def get_session():
    """
    Returns a database session object which can be used to interact with the database.
    """
    db_engine = create_engine(get_database_url())
    with Session(db_engine) as session:
        yield session
