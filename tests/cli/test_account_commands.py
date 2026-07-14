from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from pynance.database import create_session_factory
from pynance.main import app
from pynance.models.account import Account, AccountType


runner = CliRunner()


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///data/pynance.db")
    return create_session_factory(engine)


def test_accounts_create_persists_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Cash",
            "--type",
            "cash",
            "--balance",
            "20.00",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Account created" in result.output
    assert "Cash" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        account = session.scalars(select(Account)).one()

    assert account.name == "Cash"
    assert account.account_type == AccountType.CASH
    assert account.balance == Decimal("20.00")


def test_accounts_create_allows_negative_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Credit Card",
            "--type",
            "credit_card",
            "--balance",
            "-120.50",
        ],
    )

    assert result.exit_code == 0, result.output

    session_factory = _session_factory()
    with session_factory() as session:
        account = session.scalars(select(Account)).one()

    assert account.balance == Decimal("-120.50")


def test_accounts_create_rejects_duplicate_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Cash",
            "--type",
            "cash",
            "--balance",
            "20.00",
        ],
    )

    result = runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Cash",
            "--type",
            "bank",
            "--balance",
            "100.00",
        ],
    )

    assert result.exit_code != 0
    assert "Account name already exists" in result.output


def test_accounts_list_shows_accounts_table(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Cash",
            "--type",
            "cash",
            "--balance",
            "20.00",
        ],
    )
    runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            "Savings",
            "--type",
            "savings",
            "--balance",
            "50.00",
        ],
    )

    result = runner.invoke(app, ["accounts", "list"])

    assert result.exit_code == 0, result.output
    assert "Accounts" in result.output
    assert "Cash" in result.output
    assert "Savings" in result.output
    assert "20.00" in result.output
    assert "50.00" in result.output
