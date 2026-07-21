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


def _init_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output


def _create_account(
    name: str = "Cash",
    account_type: str = "cash",
    balance: str = "20.00",
) -> None:
    result = runner.invoke(
        app,
        [
            "accounts",
            "create",
            "--name",
            name,
            "--type",
            account_type,
            "--balance",
            balance,
        ],
    )
    assert result.exit_code == 0, result.output


def _get_account() -> Account:
    session_factory = _session_factory()
    with session_factory() as session:
        return session.scalars(select(Account)).one()


def test_accounts_create_persists_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

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

    account = _get_account()
    assert account.name == "Cash"
    assert account.account_type == AccountType.CASH
    assert account.balance == Decimal("20.00")


def test_accounts_create_allows_negative_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

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
    assert _get_account().balance == Decimal("-120.50")


def test_accounts_create_rejects_duplicate_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

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
    _init_database(tmp_path, monkeypatch)
    _create_account()
    _create_account("Savings", "savings", "50.00")

    result = runner.invoke(app, ["accounts", "list"])

    assert result.exit_code == 0, result.output
    assert "Accounts" in result.output
    assert "Cash" in result.output
    assert "Savings" in result.output
    assert "20.00" in result.output
    assert "50.00" in result.output


def test_accounts_show_displays_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(app, ["accounts", "show", "1"])

    assert result.exit_code == 0, result.output
    assert "Account" in result.output
    assert "Cash" in result.output
    assert "20.00" in result.output


def test_accounts_show_rejects_missing_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

    result = runner.invoke(app, ["accounts", "show", "999"])

    assert result.exit_code != 0
    assert "Account not found" in result.output


def test_accounts_update_persists_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(
        app,
        [
            "accounts",
            "update",
            "1",
            "--name",
            "  Wallet  ",
            "--type",
            "bank",
            "--balance",
            "35.50",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Account updated" in result.output
    assert "Wallet" in result.output

    account = _get_account()
    assert account.name == "Wallet"
    assert account.account_type == AccountType.BANK
    assert account.balance == Decimal("35.50")


def test_accounts_update_rejects_missing_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(app, ["accounts", "update", "1"])

    assert result.exit_code != 0
    assert "At least one field must be provided" in result.output


def test_accounts_update_rejects_empty_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(app, ["accounts", "update", "1", "--name", "   "])

    assert result.exit_code != 0
    assert "Account name cannot be empty" in result.output


def test_accounts_update_rejects_duplicate_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()
    _create_account("Savings", "savings", "50.00")

    result = runner.invoke(app, ["accounts", "update", "2", "--name", "Cash"])

    assert result.exit_code != 0
    assert "Account name already exists" in result.output


def test_accounts_update_rejects_invalid_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(app, ["accounts", "update", "1", "--balance", "nan"])

    assert result.exit_code != 0
    assert "Balance must be a finite decimal number" in result.output


def test_accounts_update_allows_negative_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account("Credit Card", "credit_card", "0.00")

    result = runner.invoke(
        app,
        ["accounts", "update", "1", "--balance", "-120.50"],
    )

    assert result.exit_code == 0, result.output
    assert _get_account().balance == Decimal("-120.50")


def test_accounts_delete_removes_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_account()

    result = runner.invoke(app, ["accounts", "delete", "1"])

    assert result.exit_code == 0, result.output
    assert "Account deleted 1" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        accounts = list(session.scalars(select(Account)).all())

    assert accounts == []


def test_accounts_delete_rejects_missing_account(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

    result = runner.invoke(app, ["accounts", "delete", "999"])

    assert result.exit_code != 0
    assert "Account not found" in result.output
