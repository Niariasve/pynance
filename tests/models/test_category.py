from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.category import Category, CategoryType


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    database_url = f"sqlite:///{tmp_path / 'pynance_test.db'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return create_session_factory(engine)


def test_category_allows_expense_type(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        category = Category(name="Food", category_type=CategoryType.EXPENSE)

        session.add(category)
        session.commit()

        assert category.category_type == CategoryType.EXPENSE


def test_category_allows_income_type(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        category = Category(name="Salary", category_type=CategoryType.INCOME)

        session.add(category)
        session.commit()

        assert category.category_type == CategoryType.INCOME


def test_category_rejects_invalid_category_type(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        category = Category(name="Invalid", category_type="transfer")

        session.add(category)

        with pytest.raises(IntegrityError):
            session.commit()


def test_category_sets_created_at_and_updated_at(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        category = Category(name="Food", category_type=CategoryType.EXPENSE)

        session.add(category)
        session.commit()

        assert category.created_at is not None
        assert category.updated_at is not None
