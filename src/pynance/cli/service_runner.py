from collections.abc import Callable
from typing import Protocol

import typer
from sqlalchemy.orm import Session

from pynance.cli.dependencies import database_session_context


class RepositoryFactory[RepositoryT](Protocol):
    def __call__(self, session: Session, /) -> RepositoryT: ...


class ServiceFactory[RepositoryT, ServiceT](Protocol):
    def __call__(self, repository: RepositoryT, /) -> ServiceT: ...


def run_service_operation[RepositoryT, ServiceT, ResultT](
    repository_factory: RepositoryFactory[RepositoryT],
    service_factory: ServiceFactory[RepositoryT, ServiceT],
    operation: Callable[[ServiceT], ResultT],
) -> ResultT:
    try:
        with database_session_context() as session:
            repository = repository_factory(session)
            service = service_factory(repository)

            return operation(service)

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None
