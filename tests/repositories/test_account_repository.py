from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.account import Account, AccountType
from pynance.repositories.account_repository import AccountRepository


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    database_url = f"sqlite:///{tmp_path / 'pynance_test.db'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)

    try:
        yield cast(sessionmaker[Session], create_session_factory(engine))
    finally:
        engine.dispose()


def test_account_repository_adds_account(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = AccountRepository(session)

        account = repository.add(
            Account(
                name="Cash",
                account_type=AccountType.CASH,
                balance=Decimal("20.00"),
            )
        )

        assert account.id is not None
        assert account.name == "Cash"


def test_account_repository_lists_all_accounts(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = AccountRepository(session)
        repository.add(
            Account(
                name="Cash",
                account_type=AccountType.CASH,
                balance=Decimal("20.00"),
            )
        )
        repository.add(
            Account(
                name="Savings",
                account_type=AccountType.SAVINGS,
                balance=Decimal("50.00"),
            )
        )

        accounts = repository.list_all()

        assert [account.name for account in accounts] == ["Cash", "Savings"]


def test_account_repository_gets_account_by_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = AccountRepository(session)
        created_account = repository.add(
            Account(
                name="Bank",
                account_type=AccountType.BANK,
                balance=Decimal("100.00"),
            )
        )

        account = repository.get_by_id(created_account.id)

        assert account is not None
        assert account.name == "Bank"


def test_account_repository_gets_account_by_name(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = AccountRepository(session)
        repository.add(
            Account(
                name="Cash",
                account_type=AccountType.CASH,
                balance=Decimal("20.00"),
            )
        )

        account = repository.get_by_name("Cash")

        assert account is not None
        assert account.name == "Cash"


def test_account_repository_deletes_account(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = AccountRepository(session)
        account = repository.add(
            Account(
                name="Cash",
                account_type=AccountType.CASH,
                balance=Decimal("20.00"),
            )
        )

        repository.delete(account)

        assert repository.get_by_id(account.id) is None
