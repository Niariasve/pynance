from collections.abc import Generator
from contextlib import contextmanager

import typer
from sqlalchemy.orm import Session

from pynance.database import DatabaseNotInitializedError, get_session


@contextmanager
def database_session_context() -> Generator[Session]:
    try:
        with get_session() as session:
            yield session

    except DatabaseNotInitializedError:
        typer.echo(
            "Database is not initialized. Run `pynance init` first.",
            err=True,
        )
        raise typer.Exit(code=1) from None
