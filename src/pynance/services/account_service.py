from decimal import Decimal

from pynance.models.account import Account, AccountType
from pynance.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def create_account(
        self, *, name: str, account_type: AccountType, balance: Decimal
    ) -> Account:
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Account name cannot be empty")

        existing_account = self._repository.get_by_name(clean_name)
        if existing_account is not None:
            raise ValueError("Account name already exists")

        account = Account(name=clean_name, account_type=account_type, balance=balance)

        return self._repository.add(account)

    def list_accounts(self) -> list[Account]:
        return self._repository.list_all()
