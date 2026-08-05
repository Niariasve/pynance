from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pynance.cli.parsers import parse_balance
from pynance.cli.service_runner import run_service_operation
from pynance.models.account import Account, AccountType
from pynance.repositories.account_repository import AccountRepository
from pynance.services.account_service import AccountService

accounts_app = typer.Typer()

console = Console()


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
    parsed_balance = parse_balance(balance)

    account = run_service_operation(
        AccountRepository,
        AccountService,
        lambda service: service.create_account(
            name=name, account_type=account_type, balance=parsed_balance
        ),
    )

    typer.echo(f"Account created {account.id}: {account.name}")


@accounts_app.command("list")
def list_accounts() -> None:
    accounts = run_service_operation(
        AccountRepository,
        AccountService,
        lambda service: service.list_accounts(),
    )

    table = _accounts_table("Accounts")

    for account in accounts:
        _add_account_row(table, account)

    console.print(table)


@accounts_app.command()
def show(account_id: Annotated[int, typer.Argument()]) -> None:
    account = run_service_operation(
        AccountRepository,
        AccountService,
        lambda service: service.get_account(account_id),
    )

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
    parsed_balance = parse_balance(balance) if balance is not None else None

    account = run_service_operation(
        AccountRepository,
        AccountService,
        lambda service: service.update_account(
            account_id,
            name=name,
            account_type=account_type,
            balance=parsed_balance,
        ),
    )

    typer.echo(f"Account updated {account.id}: {account.name}")


@accounts_app.command()
def delete(account_id: Annotated[int, typer.Argument()]) -> None:
    run_service_operation(
        AccountRepository,
        AccountService,
        lambda service: service.delete_account(account_id),
    )

    typer.echo(f"Account deleted {account_id}")
