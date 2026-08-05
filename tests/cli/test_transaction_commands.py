from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from pynance.database import create_session_factory
from pynance.main import app
from pynance.models.account import Account
from pynance.models.transaction import Transaction

runner = CliRunner()


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///data/pynance.db")
    return create_session_factory(engine)


def _init_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output


def _create_references() -> None:
    account_result = runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Cash",
            "--type",
            "cash",
            "--balance",
            "100.00",
        ],
    )
    assert account_result.exit_code == 0, account_result.output

    category_result = runner.invoke(
        app,
        [
            "categories",
            "create",
            "--name",
            "Food",
            "--type",
            "expense",
        ],
    )
    assert category_result.exit_code == 0, category_result.output


def _create_transaction(
    *,
    amount: str = "24.50",
    description: str = "Groceries",
    occurred_on: str = "2026-07-28",
) -> None:
    result = runner.invoke(
        app,
        [
            "transactions",
            "create",
            "--account-id",
            "1",
            "--category-id",
            "1",
            "--amount",
            amount,
            "--description",
            description,
            "--date",
            occurred_on,
        ],
    )
    assert result.exit_code == 0, result.output


def test_transactions_create_persists_transaction_without_changing_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()

    result = runner.invoke(
        app,
        [
            "transactions",
            "create",
            "--account-id",
            "1",
            "--category-id",
            "1",
            "--amount",
            "24.50",
            "--description",
            "  Groceries  ",
            "--date",
            "2026-07-28",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Transaction created 1" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        transaction = session.scalars(select(Transaction)).one()
        account = session.scalars(select(Account)).one()

    assert transaction.description == "Groceries"
    assert transaction.amount == Decimal("24.50")
    assert account.balance == Decimal("100.00")


def test_transactions_list_displays_required_fields_in_required_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()
    _create_transaction(description="Older", occurred_on="2026-07-27")
    _create_transaction(description="Newer", occurred_on="2026-07-28")

    result = runner.invoke(app, ["transactions", "list"])

    assert result.exit_code == 0, result.output
    assert "2026-07-28" in result.output
    assert "Newer" in result.output
    assert "Cash" in result.output
    assert "Food" in result.output
    assert "expense" in result.output
    assert "24.50" in result.output
    assert result.output.index("Newer") < result.output.index("Older")


def test_transactions_show_displays_required_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()
    _create_transaction()

    result = runner.invoke(app, ["transactions", "show", "1"])

    assert result.exit_code == 0, result.output
    for expected in [
        "1",
        "2026-07-28",
        "Groceries",
        "Cash",
        "Food",
        "expense",
        "24.50",
    ]:
        assert expected in result.output


def test_transactions_update_persists_only_provided_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()
    _create_transaction()

    result = runner.invoke(
        app,
        [
            "transactions",
            "update",
            "1",
            "--amount",
            "30.00",
            "--description",
            "  Weekly groceries  ",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Transaction updated 1" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        transaction = session.get(Transaction, 1)

    assert transaction is not None
    assert transaction.amount == Decimal("30.00")
    assert transaction.description == "Weekly groceries"
    assert transaction.account_id == 1
    assert transaction.category_id == 1


def test_transactions_delete_removes_transaction_without_changing_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()
    _create_transaction()

    result = runner.invoke(app, ["transactions", "delete", "1"])

    assert result.exit_code == 0, result.output
    assert "Transaction deleted 1" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        transaction = session.get(Transaction, 1)
        account = session.get(Account, 1)

    assert transaction is None
    assert account is not None
    assert account.balance == Decimal("100.00")


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--account-id", "999", "--category-id", "1"], "Account not found"),
        (["--account-id", "1", "--category-id", "999"], "Category not found"),
    ],
)
def test_transactions_create_surfaces_missing_reference_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    message: str,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()

    result = runner.invoke(
        app,
        [
            "transactions",
            "create",
            *arguments,
            "--amount",
            "24.50",
            "--description",
            "Groceries",
            "--date",
            "2026-07-28",
        ],
    )

    assert result.exit_code != 0
    assert message in result.output


@pytest.mark.parametrize(
    ("option", "value", "message"),
    [
        ("--amount", "not-a-decimal", "Amount must be a valid decimal number"),
        ("--date", "2026-02-30", "Invalid value for '--date'"),
    ],
)
def test_transactions_create_rejects_invalid_cli_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    option: str,
    value: str,
    message: str,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_references()
    arguments = [
        "transactions",
        "create",
        "--account-id",
        "1",
        "--category-id",
        "1",
        "--amount",
        "24.50",
        "--description",
        "Groceries",
        "--date",
        "2026-07-28",
    ]
    arguments[arguments.index(option) + 1] = value

    result = runner.invoke(app, arguments)

    assert result.exit_code != 0
    assert message in result.output
