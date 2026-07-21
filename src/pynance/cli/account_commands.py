from decimal import Decimal, InvalidOperation
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pynance.cli.dependencies import database_session_context
from pynance.models.account import AccountType
from pynance.repositories.account_repository import AccountRepository
from pynance.services.account_service import AccountService

accounts_app = typer.Typer()

console = Console()


@accounts_app.command()
def create(
    name: Annotated[str, typer.Option()],
    account_type: Annotated[AccountType, typer.Option("--type")],
    balance: Annotated[str, typer.Option()] = "0.0",
) -> None:
    try:
        parsed_balance = Decimal(balance)
    except InvalidOperation:
        raise typer.BadParameter("Balance must be a valid decimal number") from None

    if not parsed_balance.is_finite():
        raise typer.BadParameter("Balance must be a finite decimal number")

    try:
        with database_session_context() as session:
            repository = AccountRepository(session)
            service = AccountService(repository)

            account = service.create_account(
                name=name, account_type=account_type, balance=parsed_balance
            )

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None

    typer.echo(f"Account created {account.id}: {account.name}")


@accounts_app.command("list")
def list_accounts() -> None:
    with database_session_context() as session:
        repository = AccountRepository(session)
        service = AccountService(repository)

        accounts = service.list_accounts()

    table = Table(title="Accounts")

    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Balance", justify="right")

    for account in accounts:
        table.add_row(
            str(account.id),
            account.name,
            account.account_type,
            f"{account.balance:.2f}",
        )

    console.print(table)
