from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType


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


def test_account_allows_positive_balance(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account = Account(
            name="Cash",
            account_type=AccountType.CASH,
            balance=Decimal("20.00"),
        )

        session.add(account)
        session.commit()

        assert account.balance == Decimal("20.00")


def test_account_allows_zero_balance(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account = Account(
            name="Bank",
            account_type=AccountType.BANK,
            balance=Decimal("0.00"),
        )

        session.add(account)
        session.commit()

        assert account.balance == Decimal("0.00")


def test_account_allows_negative_balance(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account = Account(
            name="Credit Card",
            account_type=AccountType.CREDIT_CARD,
            balance=Decimal("-120.50"),
        )

        session.add(account)
        session.commit()

        assert account.balance == Decimal("-120.50")


def test_account_rejects_invalid_account_type(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account = Account(
            name="Invalid",
            account_type="investment",
            balance=Decimal("10.00"),
        )

        session.add(account)

        with pytest.raises(IntegrityError):
            session.commit()


def test_account_sets_created_at_and_updated_at(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account = Account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("100.00"),
        )

        session.add(account)
        session.commit()

        assert account.created_at is not None
        assert account.updated_at is not None
