from collections.abc import Callable
from typing import Protocol

import typer
from sqlalchemy.orm import Session

from pynance.cli.dependencies import database_session_context


class RepositoryFactory[RepositoryT](Protocol):
    def __call__(self, session: Session, /) -> RepositoryT: ...


class ServiceFactory[ServiceT](Protocol):
    def __call__(self, session: Session, /) -> ServiceT: ...


def run_service_operation[ServiceT, ResultT](
    service_factory: ServiceFactory[ServiceT],
    operation: Callable[[ServiceT], ResultT],
) -> ResultT:
    try:
        with database_session_context() as session:
            service = service_factory(session)

            return operation(service)

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None
