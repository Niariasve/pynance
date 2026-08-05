from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import Engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType
from pynance.models.category import Category, CategoryType
from pynance.models.transaction import Transaction


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


def create_account_and_category(session: Session) -> tuple[Account, Category]:
    account = Account(
        name="Cash", account_type=AccountType.CASH, balance=Decimal("0.00")
    )
    category = Category(name="Food", category_type=CategoryType.EXPENSE)
    session.add_all([account, category])
    session.flush()
    return account, category


def create_transaction(session: Session) -> tuple[Transaction, Account, Category]:
    account, category = create_account_and_category(session)
    transaction = Transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )
    session.add(transaction)
    session.flush()
    return transaction, account, category


def test_transaction_persists_a_positive_amount_and_calendar_date(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        transaction, _, _ = create_transaction(session)
        session.commit()

        assert transaction.amount == Decimal("24.50")
        assert transaction.occurred_on == date(2026, 7, 28)


@pytest.mark.parametrize("amount", [Decimal("0.00"), Decimal("-1.00")])
def test_transaction_rejects_non_positive_amounts(
    session_factory: sessionmaker[Session], amount: Decimal
) -> None:
    with session_factory() as session:
        account, category = create_account_and_category(session)
        transaction = Transaction(
            account_id=account.id,
            category_id=category.id,
            amount=amount,
            description="Groceries",
            occurred_on=date(2026, 7, 28),
        )
        session.add(transaction)

        with pytest.raises(IntegrityError):
            session.commit()


def test_transaction_rejects_blank_description(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account, category = create_account_and_category(session)
        transaction = Transaction(
            account_id=account.id,
            category_id=category.id,
            amount=Decimal("24.50"),
            description="   ",
            occurred_on=date(2026, 7, 28),
        )
        session.add(transaction)

        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize(
    ("account_id", "category_id"),
    [(999, 1), (1, 999)],
)
def test_transaction_rejects_missing_references(
    session_factory: sessionmaker[Session],
    account_id: int,
    category_id: int,
) -> None:
    with session_factory() as session:
        account, category = create_account_and_category(session)
        transaction = Transaction(
            account_id=account_id if account_id == 999 else account.id,
            category_id=category_id if category_id == 999 else category.id,
            amount=Decimal("24.50"),
            description="Groceries",
            occurred_on=date(2026, 7, 28),
        )
        session.add(transaction)

        with pytest.raises(IntegrityError):
            session.commit()


def test_transaction_prevents_deleting_a_referenced_account(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        _, account, _ = create_transaction(session)
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(delete(Account).where(Account.id == account.id))


def test_transaction_prevents_deleting_a_referenced_category(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        _, _, category = create_transaction(session)
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(delete(Category).where(Category.id == category.id))
