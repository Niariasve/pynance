from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType
from pynance.models.category import Category, CategoryType
from pynance.models.transaction import Transaction
from pynance.repositories.transaction_repository import TransactionRepository


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    engine = create_engine_from_url(f"sqlite:///{tmp_path / 'pynance_test.db'}")
    init_db(engine)

    try:
        yield create_session_factory(engine)
    finally:
        engine.dispose()


def _references(session: Session) -> tuple[Account, Category]:
    account = Account(
        name="Cash", account_type=AccountType.CASH, balance=Decimal("100.00")
    )
    category = Category(name="Food", category_type=CategoryType.EXPENSE)
    session.add_all([account, category])
    session.commit()
    return account, category


def _transaction(
    account: Account,
    category: Category,
    *,
    amount: str = "24.50",
    description: str = "Groceries",
    occurred_on: date = date(2026, 7, 28),
) -> Transaction:
    return Transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal(amount),
        description=description,
        occurred_on=occurred_on,
    )


def test_transaction_repository_supports_add_and_get_by_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account, category = _references(session)
        repository = TransactionRepository(session)

        created = repository.add(_transaction(account, category))
        retrieved = repository.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.description == "Groceries"


def test_transaction_repository_lists_newest_date_then_highest_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account, category = _references(session)
        repository = TransactionRepository(session)
        oldest = repository.add(
            _transaction(
                account,
                category,
                description="Oldest",
                occurred_on=date(2026, 7, 27),
            )
        )
        first_same_day = repository.add(
            _transaction(account, category, description="First same day")
        )
        second_same_day = repository.add(
            _transaction(account, category, description="Second same day")
        )

        transactions = repository.list_all()

        assert [transaction.id for transaction in transactions] == [
            second_same_day.id,
            first_same_day.id,
            oldest.id,
        ]


def test_transaction_repository_supports_update(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account, category = _references(session)
        repository = TransactionRepository(session)
        transaction = repository.add(_transaction(account, category))

        transaction.amount = Decimal("30.00")
        updated = repository.update(transaction)

        assert updated.amount == Decimal("30.00")
        persisted = repository.get_by_id(transaction.id)
        assert persisted is not None
        assert persisted.amount == Decimal("30.00")


def test_transaction_repository_supports_delete(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        account, category = _references(session)
        repository = TransactionRepository(session)
        transaction = repository.add(_transaction(account, category))

        repository.delete(transaction)

        assert repository.get_by_id(transaction.id) is None
