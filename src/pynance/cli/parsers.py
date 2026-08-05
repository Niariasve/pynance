import re
from datetime import date
from decimal import Decimal, InvalidOperation

import typer


def parse_balance(balance: str) -> Decimal:
    try:
        parsed_balance = Decimal(balance)
    except InvalidOperation:
        raise typer.BadParameter("Balance must be a valid decimal number") from None

    if not parsed_balance.is_finite():
        raise typer.BadParameter("Balance must be a finite decimal number")

    return parsed_balance


def parse_iso_date(value: str) -> date:
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        raise typer.BadParameter("Date must be a valid date in YYYY-mm-dd format")

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise typer.BadParameter(
            "Date must be a valid date in YYYY-mm-dd format"
        ) from None
