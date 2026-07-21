from decimal import Decimal, InvalidOperation
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pynance.cli.dependencies import database_session_context
from pynance.models.account import Account, AccountType
from pynance.repositories.account_repository import AccountRepository
from pynance.services.account_service import AccountService

accounts_app = typer.Typer()

console = Console()


def _parse_balance(balance: str) -> Decimal:
    try:
        parsed_balance = Decimal(balance)
    except InvalidOperation:
        raise typer.BadParameter("Balance must be a valid decimal number") from None

    if not parsed_balance.is_finite():
        raise typer.BadParameter("Balance must be a finite decimal number")

    return parsed_balance


def _accounts_table(title: str) -> Table:
    table = Table(title=title)

    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Balance", justify="right")

    return table


def _add_account_row(table: Table, account: Account) -> None:
    table.add_row(
        str(account.id),
        account.name,
        account.account_type,
        f"{account.balance:.2f}",
    )


@accounts_app.command()
def create(
    name: Annotated[str, typer.Option()],
    account_type: Annotated[AccountType, typer.Option("--type")],
    balance: Annotated[str, typer.Option()] = "0.0",
) -> None:
    parsed_balance = _parse_balance(balance)

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

    table = _accounts_table("Accounts")

    for account in accounts:
        _add_account_row(table, account)

    console.print(table)


@accounts_app.command()
def show(account_id: Annotated[int, typer.Argument()]) -> None:
    try:
        with database_session_context() as session:
            repository = AccountRepository(session)
            service = AccountService(repository)

            account = service.get_account(account_id)

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None

    table = _accounts_table("Account")
    _add_account_row(table, account)
    console.print(table)


@accounts_app.command()
def update(
    account_id: Annotated[int, typer.Argument()],
    name: Annotated[str | None, typer.Option()] = None,
    account_type: Annotated[AccountType | None, typer.Option("--type")] = None,
    balance: Annotated[str | None, typer.Option()] = None,
) -> None:
    parsed_balance = _parse_balance(balance) if balance is not None else None

    try:
        with database_session_context() as session:
            repository = AccountRepository(session)
            service = AccountService(repository)

            account = service.update_account(
                account_id,
                name=name,
                account_type=account_type,
                balance=parsed_balance,
            )

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None

    typer.echo(f"Account updated {account.id}: {account.name}")


@accounts_app.command()
def delete(account_id: Annotated[int, typer.Argument()]) -> None:
    try:
        with database_session_context() as session:
            repository = AccountRepository(session)
            service = AccountService(repository)

            service.delete_account(account_id)

    except ValueError as error:
        raise typer.BadParameter(str(error)) from None

    typer.echo(f"Account deleted {account_id}")
