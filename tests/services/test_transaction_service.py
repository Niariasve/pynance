from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType
from pynance.models.category import Category, CategoryType
from pynance.repositories.account_repository import AccountRepository
from pynance.repositories.category_repository import CategoryRepository
from pynance.repositories.transaction_repository import TransactionRepository
from pynance.services.transaction_service import TransactionService

TransactionContext = tuple[
    TransactionService,
    AccountRepository,
    CategoryRepository,
]


@pytest.fixture
def transaction_context(tmp_path: Path) -> Iterator[TransactionContext]:
    engine = create_engine_from_url(f"sqlite:///{tmp_path / 'pynance_test.db'}")
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            transaction_repository = TransactionRepository(session)
            account_repository = AccountRepository(session)
            category_repository = CategoryRepository(session)
            yield (
                TransactionService(
                    transaction_repository,
                    account_repository,
                    category_repository,
                ),
                account_repository,
                category_repository,
            )
    finally:
        engine.dispose()


def _references(
    account_repository: AccountRepository,
    category_repository: CategoryRepository,
) -> tuple[Account, Category]:
    account = account_repository.add(
        Account(
            name="Cash",
            account_type=AccountType.CASH,
            balance=Decimal("100.00"),
        )
    )
    category = category_repository.add(
        Category(name="Food", category_type=CategoryType.EXPENSE)
    )
    return account, category


def test_transaction_service_creates_and_normalizes_transaction(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)

    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="  Groceries  ",
        occurred_on=date(2026, 7, 28),
    )

    assert transaction.id is not None
    assert transaction.description == "Groceries"
    assert transaction.amount == Decimal("24.50")
    assert transaction.occurred_on == date(2026, 7, 28)
    assert transaction.account_id == account.id
    assert transaction.category_id == category.id


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("1.001"),
    ],
)
def test_transaction_service_rejects_invalid_amounts(
    transaction_context: TransactionContext,
    amount: Decimal,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)

    with pytest.raises(ValueError):
        service.create_transaction(
            account_id=account.id,
            category_id=category.id,
            amount=amount,
            description="Groceries",
            occurred_on=date(2026, 7, 28),
        )


def test_transaction_service_rejects_empty_description(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)

    with pytest.raises(ValueError, match="Description cannot be empty"):
        service.create_transaction(
            account_id=account.id,
            category_id=category.id,
            amount=Decimal("24.50"),
            description="   ",
            occurred_on=date(2026, 7, 28),
        )


def test_transaction_service_rejects_missing_account(
    transaction_context: TransactionContext,
) -> None:
    service, _, category_repository = transaction_context
    category = category_repository.add(
        Category(name="Food", category_type=CategoryType.EXPENSE)
    )

    with pytest.raises(ValueError, match="Account not found"):
        service.create_transaction(
            account_id=999,
            category_id=category.id,
            amount=Decimal("24.50"),
            description="Groceries",
            occurred_on=date(2026, 7, 28),
        )


def test_transaction_service_rejects_missing_category(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, _ = transaction_context
    account = account_repository.add(
        Account(
            name="Cash",
            account_type=AccountType.CASH,
            balance=Decimal("100.00"),
        )
    )

    with pytest.raises(ValueError, match="Category not found"):
        service.create_transaction(
            account_id=account.id,
            category_id=999,
            amount=Decimal("24.50"),
            description="Groceries",
            occurred_on=date(2026, 7, 28),
        )


def test_transaction_service_rejects_missing_transaction(
    transaction_context: TransactionContext,
) -> None:
    service, _, _ = transaction_context

    with pytest.raises(ValueError, match="Transaction not found"):
        service.get_transaction(999)


def test_transaction_service_updates_only_the_provided_field(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)
    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )

    updated = service.update_transaction(transaction.id, amount=Decimal("30.00"))

    assert updated.amount == Decimal("30.00")
    assert updated.description == "Groceries"
    assert updated.account_id == account.id
    assert updated.category_id == category.id


def test_transaction_service_updates_relationships_and_normalizes_description(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)
    other_account = account_repository.add(
        Account(
            name="Bank",
            account_type=AccountType.BANK,
            balance=Decimal("200.00"),
        )
    )
    other_category = category_repository.add(
        Category(name="Salary", category_type=CategoryType.INCOME)
    )
    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )

    updated = service.update_transaction(
        transaction.id,
        account_id=other_account.id,
        category_id=other_category.id,
        description="  Salary payment  ",
        occurred_on=date(2026, 7, 29),
    )

    assert updated.account_id == other_account.id
    assert updated.category_id == other_category.id
    assert updated.description == "Salary payment"
    assert updated.occurred_on == date(2026, 7, 29)


def test_transaction_service_rejects_update_without_fields(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)
    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )

    with pytest.raises(ValueError, match="At least one field must be provided"):
        service.update_transaction(transaction.id)


def test_transaction_service_deletes_transaction(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)
    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )

    service.delete_transaction(transaction.id)

    with pytest.raises(ValueError, match="Transaction not found"):
        service.get_transaction(transaction.id)


def test_transaction_operations_do_not_change_account_balance(
    transaction_context: TransactionContext,
) -> None:
    service, account_repository, category_repository = transaction_context
    account, category = _references(account_repository, category_repository)

    transaction = service.create_transaction(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("24.50"),
        description="Groceries",
        occurred_on=date(2026, 7, 28),
    )
    service.update_transaction(transaction.id, amount=Decimal("30.00"))
    service.delete_transaction(transaction.id)

    persisted_account = account_repository.get_by_id(account.id)
    assert persisted_account is not None
    assert persisted_account.balance == Decimal("100.00")
