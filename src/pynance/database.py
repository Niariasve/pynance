from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_PATH = Path("data/pynance.db")
DATABASE_URL = f"sqlite+pysqlite:///{DATABASE_PATH}"


class Base(DeclarativeBase):
    pass

class DatabaseNotInitializedError(Exception):
    pass


def create_engine_from_url(database_url: str) -> Engine:
    return create_engine(database_url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session]:
    if not DATABASE_PATH.exists():
        raise DatabaseNotInitializedError

    engine = create_engine_from_url(DATABASE_URL)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            yield session

    finally:
        engine.dispose()
