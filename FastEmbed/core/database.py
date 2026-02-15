from sqlmodel import SQLModel, Session, create_engine


from FastEmbed.config import Config


def get_database_url():
    return Config.DATABASE_URL


async def init_database():
    """
    Creates all tables in the database using the definitions in the SQLModel metadata.
    """
    print("Initializing database...")
    db_engine = create_engine(
        get_database_url(), connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(db_engine)


async def get_session():
    """
    Returns a database session object which can be used to interact with the database.
    """
    db_engine = create_engine(
        get_database_url(), connect_args={"check_same_thread": False}
    )
    with Session(db_engine) as session:
        yield session
