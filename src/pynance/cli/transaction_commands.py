from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from pynance.cli.parsers import parse_amount, parse_iso_date
from pynance.cli.service_runner import run_service_operation
from pynance.models.transaction import Transaction
from pynance.repositories.account_repository import AccountRepository
from pynance.repositories.category_repository import CategoryRepository
from pynance.repositories.transaction_repository import TransactionRepository
from pynance.services.transaction_service import TransactionService

transactions_app = typer.Typer()

console = Console()


def _transaction_service(session: Session) -> TransactionService:
    return TransactionService(
        TransactionRepository(session),
        AccountRepository(session),
        CategoryRepository(session),
    )


def _transactions_table(title: str) -> Table:
    table = Table(title=title)

    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Description")
    table.add_column("Account")
    table.add_column("Category")
    table.add_column("Type")
    table.add_column("Amount", justify="right")

    return table


def _add_transaction_row(table: Table, transaction: Transaction) -> None:
    table.add_row(
        str(transaction.id),
        f"{transaction.occurred_on.isoformat()}",
        transaction.description,
        transaction.account.name,
        transaction.category.name,
        transaction.category.category_type,
        f"{transaction.amount:.2f}",
    )


@transactions_app.command()
def create(
    account_id: Annotated[int, typer.Option("--account-id")],
    category_id: Annotated[int, typer.Option("--category-id")],
    description: Annotated[str, typer.Option()],
    occurred_on: Annotated[str, typer.Option("--date")],
    amount: Annotated[str, typer.Option()],
) -> None:
    parsed_amount = parse_amount(amount)
    parsed_occurred_on = parse_iso_date(occurred_on)

    transaction = run_service_operation(
        _transaction_service,
        lambda service: service.create_transaction(
            account_id=account_id,
            category_id=category_id,
            amount=parsed_amount,
            description=description,
            occurred_on=parsed_occurred_on,
        ),
    )

    typer.echo(f"Transaction created {transaction.id}")


@transactions_app.command()
def list() -> None:
    transactions = run_service_operation(
        _transaction_service,
        lambda service: service.list_transactions(),
    )

    table = _transactions_table("Transactions")

    for transaction in transactions:
        _add_transaction_row(table, transaction)

    console.print(table)


@transactions_app.command()
def show(transaction_id: Annotated[int, typer.Argument()]) -> None:
    transaction = run_service_operation(
        _transaction_service, lambda service: service.get_transaction(transaction_id)
    )

    table = _transactions_table("Transactions")
    _add_transaction_row(table, transaction)
    console.print(table)


@transactions_app.command()
def update(
    transaction_id: Annotated[int, typer.Argument()],
    account_id: Annotated[int | None, typer.Option("--account-id")] = None,
    category_id: Annotated[int | None, typer.Option("--category-id")] = None,
    description: Annotated[str | None, typer.Option()] = None,
    occurred_on: Annotated[str | None, typer.Option("--date")] = None,
    amount: Annotated[str | None, typer.Option()] = None,
) -> None:
    parsed_amount = parse_amount(amount) if amount is not None else None
    parsed_occurred_on = (
        parse_iso_date(occurred_on) if occurred_on is not None else None
    )

    transaction = run_service_operation(
        _transaction_service,
        lambda service: service.update_transaction(
            transaction_id,
            account_id=account_id,
            category_id=category_id,
            description=description,
            occurred_on=parsed_occurred_on,
            amount=parsed_amount,
        ),
    )

    typer.echo(f"Transaction updated {transaction.id}")


@transactions_app.command()
def delete(transaction_id: Annotated[int, typer.Argument()]) -> None:
    run_service_operation(
        _transaction_service, lambda service: service.delete_transaction(transaction_id)
    )

    typer.echo(f"Transaction deleted {transaction_id}")
