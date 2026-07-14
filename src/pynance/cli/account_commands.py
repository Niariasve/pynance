from decimal import Decimal
from typing import Annotated

import typer

accounts_app = typer.Typer()


@accounts_app.command()
def create(
    name: str,
    type: Annotated[str, typer.Option()],
    balance: Annotated[float, typer.Option()],
) -> None:
    print(f"{name} | {type} | {balance}")
