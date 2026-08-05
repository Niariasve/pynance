from decimal import Decimal
from typing import Annotated

from pynance.cli.parsers import parse_balance, parse_iso_date
from pynance.cli.service_runner import run_service_operation
from pynance.repositories.transaction_repository import TransactionRepository
from pynance.services.transaction_service import TransactionService
import typer
from rich.console import Console
from rich.table import Table

from pynance.models.transaction import Transaction

transactions_app = typer.Typer()

console = Console()


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
        f"{transaction.occurred_on.isoformat}",
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
    parsed_amount = parse_balance(amount)
    parsed_occurred_on = parse_iso_date(occurred_on)

    transaction = run_service_operation(
        TransactionRepository,
        TransactionService,
        lambda service: service.create_transaction(
            account_id=account_id,
            category_id=category_id,
            amount=parsed_amount,
            description=description,
            occurred_on=parsed_occurred_on
        )
    )

    typer.echo(f"Transaction created {transaction.id}")
