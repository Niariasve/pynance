from datetime import date
from decimal import Decimal

from pynance.models.account import Account
from pynance.models.category import Category
from pynance.models.transaction import Transaction
from pynance.repositories.account_repository import AccountRepository
from pynance.repositories.category_repository import CategoryRepository
from pynance.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._transaction_repository = transaction_repository
        self._account_repository = account_repository
        self._category_repository = category_repository

    def create_transaction(
        self,
        *,
        account_id: int,
        category_id: int,
        amount: Decimal,
        description: str,
        occurred_on: date,
    ) -> Transaction:
        clean_description = description.strip()
        if not clean_description:
            raise ValueError("Description cannot be empty")

        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be finite positive number")

        cent = Decimal("0.01")
        if amount != amount.quantize(cent):
            raise ValueError("Amount must have at most two decimals")

        if self._existing_account(account_id) is None:
            raise ValueError("Account not found")

        if self._existing_category(category_id) is None:
            raise ValueError("Category not found")

        transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            description=clean_description,
            occurred_on=occurred_on,
        )

        return self._transaction_repository.add(transaction)

    def list_transactions(self) -> list[Transaction]:
        return self._transaction_repository.list_all()

    def get_transaction(self, transaction_id: int) -> Transaction:
        transaction = self._transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise ValueError("Transaction not found")

        return transaction

    def update_transaction(
        self,
        transaction_id: int,
        *,
        account_id: int | None,
        category_id: int | None,
        amount: Decimal | None,
        description: str | None,
        occurred_on: date | None,
    ) -> Transaction:
        if (
            account_id is None
            and category_id is None
            and amount is None
            and description is None
            and occurred_on is None
        ):
            raise ValueError("At least one field must be provided")

            transaction = self.get_transaction(transaction_id)

            if description is not None:
                clean_description = description.strip()
                

    def _existing_account(self, account_id: int) -> Account | None:
        return self._account_repository.get_by_id(account_id)

    def _existing_category(self, category_id: int) -> Category | None:
        return self._category_repository.get_by_id(category_id)
