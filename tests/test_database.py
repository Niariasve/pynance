from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import Engine, inspect, select
from sqlalchemy.orm import Session

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType
from pynance.models.category import Category, CategoryType


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'pynance_test.db'}"


@pytest.fixture
def engine(database_url: str) -> Iterator[Engine]:
    engine = create_engine_from_url(database_url)
    try:
        yield engine
    finally:
        engine.dispose()


def test_init_db_creates_accounts_table(engine: Engine) -> None:
    init_db(engine)

    inspector = inspect(engine)

    assert "accounts" in inspector.get_table_names()


def test_init_db_creates_categories_table(engine: Engine) -> None:
    init_db(engine)

    inspector = inspect(engine)

    assert "categories" in inspector.get_table_names()


def test_init_db_creates_transactions_table(engine: Engine) -> None:
    init_db(engine)

    inspector = inspect(engine)

    assert "transactions" in inspector.get_table_names()


def test_session_factory_can_persist_and_read_accounts(engine: Engine) -> None:
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(
            Account(
                name="Cash",
                account_type=AccountType.CASH,
                balance=Decimal("20.00"),
            )
        )
        session.commit()

    with session_factory() as session:
        account = session.scalars(select(Account)).one()

    assert account.name == "Cash"
    assert account.account_type == AccountType.CASH
    assert account.balance == Decimal("20.00")


def test_session_factory_can_persist_and_read_categories(engine: Engine) -> None:
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(Category(name="Food", category_type=CategoryType.EXPENSE))
        session.commit()

    with session_factory() as session:
        category = session.scalars(select(Category)).one()

    assert category.name == "Food"
    assert category.category_type == CategoryType.EXPENSE


def test_session_factory_expires_nothing_on_commit(engine: Engine) -> None:
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        account = Account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("50.00"),
        )
        session.add(account)
        session.commit()

        assert account.name == "Savings"


def test_database_helpers_do_not_require_global_state(database_url: str) -> None:
    first_engine = create_engine_from_url(database_url)
    second_engine = create_engine_from_url(database_url)

    try:
        assert first_engine is not second_engine
        assert str(first_engine.url) == database_url
        assert str(second_engine.url) == database_url
    finally:
        first_engine.dispose()
        second_engine.dispose()


def test_create_session_factory_returns_sqlalchemy_sessions(engine: Engine) -> None:
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        assert isinstance(session, Session)
