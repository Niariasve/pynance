from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from pynance.database import create_session_factory
from pynance.main import app
from pynance.models.category import Category, CategoryType

runner = CliRunner()


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///data/pynance.db")
    return create_session_factory(engine)


def _init_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output


def _create_category(
    name: str = "Food",
    category_type: str = "expense",
) -> None:
    result = runner.invoke(
        app,
        [
            "categories",
            "create",
            "--name",
            name,
            "--type",
            category_type,
        ],
    )
    assert result.exit_code == 0, result.output


def _get_category() -> Category:
    session_factory = _session_factory()
    with session_factory() as session:
        return session.scalars(select(Category)).one()


def test_categories_create_persists_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

    result = runner.invoke(
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

    assert result.exit_code == 0, result.output
    assert "Category created" in result.output
    assert "Food" in result.output

    category = _get_category()
    assert category.name == "Food"
    assert category.category_type == CategoryType.EXPENSE


def test_categories_create_rejects_duplicate_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(
        app,
        [
            "categories",
            "create",
            "--name",
            "Food",
            "--type",
            "income",
        ],
    )

    assert result.exit_code != 0
    assert "Category name already exists" in result.output


def test_categories_list_shows_categories_table(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()
    _create_category("Salary", "income")

    result = runner.invoke(app, ["categories", "list"])

    assert result.exit_code == 0, result.output
    assert "Categories" in result.output
    assert "Food" in result.output
    assert "Salary" in result.output
    assert "expense" in result.output
    assert "income" in result.output


def test_categories_show_displays_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(app, ["categories", "show", "1"])

    assert result.exit_code == 0, result.output
    assert "Category" in result.output
    assert "Food" in result.output
    assert "expense" in result.output


def test_categories_show_rejects_missing_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

    result = runner.invoke(app, ["categories", "show", "999"])

    assert result.exit_code != 0
    assert "Category not found" in result.output


def test_categories_update_persists_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(
        app,
        [
            "categories",
            "update",
            "1",
            "--name",
            "  Groceries  ",
            "--type",
            "expense",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Category updated" in result.output
    assert "Groceries" in result.output

    category = _get_category()
    assert category.name == "Groceries"
    assert category.category_type == CategoryType.EXPENSE


def test_categories_update_rejects_missing_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(app, ["categories", "update", "1"])

    assert result.exit_code != 0
    assert "At least one field must be provided" in result.output


def test_categories_update_rejects_empty_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(app, ["categories", "update", "1", "--name", "   "])

    assert result.exit_code != 0
    assert "Category name cannot be empty" in result.output


def test_categories_update_rejects_duplicate_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()
    _create_category("Salary", "income")

    result = runner.invoke(app, ["categories", "update", "2", "--name", "Food"])

    assert result.exit_code != 0
    assert "Category name already exists" in result.output


def test_categories_delete_removes_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)
    _create_category()

    result = runner.invoke(app, ["categories", "delete", "1"])

    assert result.exit_code == 0, result.output
    assert "Category deleted 1" in result.output

    session_factory = _session_factory()
    with session_factory() as session:
        categories = list(session.scalars(select(Category)).all())

    assert categories == []


def test_categories_delete_rejects_missing_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_database(tmp_path, monkeypatch)

    result = runner.invoke(app, ["categories", "delete", "999"])

    assert result.exit_code != 0
    assert "Category not found" in result.output
