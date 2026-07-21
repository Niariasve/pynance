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

    def get_account(self, account_id: int) -> Account:
        account = self._repository.get_by_id(account_id)
        if account is None:
            raise ValueError("Account not found")

        return account

    def update_account(
        self,
        account_id: int,
        *,
        name: str | None = None,
        account_type: AccountType | None = None,
        balance: Decimal | None = None,
    ) -> Account:
        if name is None and account_type is None and balance is None:
            raise ValueError("At least one field must be provided")

        account = self.get_account(account_id)

        if name is not None:
            clean_name = name.strip()

            if not clean_name:
                raise ValueError("Account name cannot be empty")

            existing_account = self._repository.get_by_name(clean_name)
            if existing_account is not None and existing_account.id != account.id:
                raise ValueError("Account name already exists")

            account.name = clean_name

        if account_type is not None:
            account.account_type = account_type
        if balance is not None:
            account.balance = balance

        return self._repository.update(account)

    def delete_account(self, account_id: int) -> None:
        account = self.get_account(account_id)
        self._repository.delete(account)
