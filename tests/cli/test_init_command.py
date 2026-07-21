from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect
from typer.testing import CliRunner

from pynance.main import app

runner = CliRunner()


def test_init_command_creates_database_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])
    database_path = Path("data/pynance.db")

    assert result.exit_code == 0, result.output
    assert database_path.exists()
    assert "Database initialized" in result.output


def test_init_command_creates_accounts_table(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0, result.output

    database_url = "sqlite:///data/pynance.db"
    engine = create_engine(database_url)

    try:
        inspector = inspect(engine)

        assert "accounts" in inspector.get_table_names()
    finally:
        engine.dispose()


def test_init_command_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(app, ["init"])
    second_result = runner.invoke(app, ["init"])

    assert first_result.exit_code == 0, first_result.output
    assert second_result.exit_code == 0, second_result.output
    assert Path("data/pynance.db").exists()
