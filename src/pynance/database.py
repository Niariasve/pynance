from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pynance.models import import_models

DATABASE_PATH = Path("data/pynance.db")
DATABASE_URL = f"sqlite+pysqlite:///{DATABASE_PATH}"


class Base(DeclarativeBase):
    pass


class DatabaseNotInitializedError(Exception):
    pass


def create_engine_from_url(database_url: str) -> Engine:
    engine = create_engine(database_url)

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(
            dbapi_connection: Any, _connection_record: Any
        ) -> None:
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )


def init_db(engine: Engine) -> None:
    import_models()
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
