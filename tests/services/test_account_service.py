from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import AccountType
from pynance.repositories.account_repository import AccountRepository
from pynance.services.account_service import AccountService


@pytest.fixture
def account_service(tmp_path: Path) -> Iterator[AccountService]:
    database_url = f"sqlite:///{tmp_path / 'pynance_test.db'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            yield AccountService(AccountRepository(session))
    finally:
        engine.dispose()


def test_account_service_creates_account(account_service: AccountService) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    assert account.id is not None
    assert account.name == "Cash"
    assert account.account_type == AccountType.CASH
    assert account.balance == Decimal("20.00")


def test_account_service_allows_negative_initial_balance(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="Credit Card",
        account_type=AccountType.CREDIT_CARD,
        balance=Decimal("-120.50"),
    )

    assert account.balance == Decimal("-120.50")


def test_account_service_strips_account_name(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="  Cash  ",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    assert account.name == "Cash"


def test_account_service_rejects_empty_account_name(
    account_service: AccountService,
) -> None:
    with pytest.raises(ValueError, match="Account name cannot be empty"):
        account_service.create_account(
            name="   ",
            account_type=AccountType.CASH,
            balance=Decimal("20.00"),
        )


def test_account_service_rejects_duplicate_account_name(
    account_service: AccountService,
) -> None:
    account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    with pytest.raises(ValueError, match="Account name already exists"):
        account_service.create_account(
            name="Cash",
            account_type=AccountType.BANK,
            balance=Decimal("100.00"),
        )


def test_account_service_lists_accounts(account_service: AccountService) -> None:
    account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )
    account_service.create_account(
        name="Savings",
        account_type=AccountType.SAVINGS,
        balance=Decimal("50.00"),
    )

    accounts = account_service.list_accounts()

    assert [account.name for account in accounts] == ["Cash", "Savings"]


def test_account_service_gets_account(account_service: AccountService) -> None:
    created_account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    account = account_service.get_account(created_account.id)

    assert account.name == "Cash"


def test_account_service_rejects_missing_account(
    account_service: AccountService,
) -> None:
    with pytest.raises(ValueError, match="Account not found"):
        account_service.get_account(999)


def test_account_service_updates_account(account_service: AccountService) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    updated_account = account_service.update_account(
        account.id,
        name="  Wallet  ",
        account_type=AccountType.BANK,
        balance=Decimal("35.50"),
    )

    assert updated_account.name == "Wallet"
    assert updated_account.account_type == AccountType.BANK
    assert updated_account.balance == Decimal("35.50")


def test_account_service_allows_negative_updated_balance(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="Credit Card",
        account_type=AccountType.CREDIT_CARD,
        balance=Decimal("0.00"),
    )

    updated_account = account_service.update_account(
        account.id,
        balance=Decimal("-120.50"),
    )

    assert updated_account.balance == Decimal("-120.50")


def test_account_service_rejects_update_without_fields(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    with pytest.raises(ValueError, match="At least one field must be provided"):
        account_service.update_account(account.id)


def test_account_service_rejects_empty_updated_account_name(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    with pytest.raises(ValueError, match="Account name cannot be empty"):
        account_service.update_account(account.id, name="   ")


def test_account_service_rejects_duplicate_updated_account_name(
    account_service: AccountService,
) -> None:
    account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )
    savings_account = account_service.create_account(
        name="Savings",
        account_type=AccountType.SAVINGS,
        balance=Decimal("50.00"),
    )

    with pytest.raises(ValueError, match="Account name already exists"):
        account_service.update_account(savings_account.id, name="Cash")


def test_account_service_allows_unchanged_updated_account_name(
    account_service: AccountService,
) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    updated_account = account_service.update_account(account.id, name="Cash")

    assert updated_account.name == "Cash"


def test_account_service_deletes_account(account_service: AccountService) -> None:
    account = account_service.create_account(
        name="Cash",
        account_type=AccountType.CASH,
        balance=Decimal("20.00"),
    )

    account_service.delete_account(account.id)

    with pytest.raises(ValueError, match="Account not found"):
        account_service.get_account(account.id)
