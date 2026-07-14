from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass

def create_engine_from_url(database_url: str) -> Engine:
    return create_engine(database_url)

def create_session_factory(engine: Engine) -> Session:
    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)