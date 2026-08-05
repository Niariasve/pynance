from sqlalchemy import select
from sqlalchemy.orm import Session

from pynance.models.transaction import Transaction
from pynance.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Transaction)

    def list_all(self) -> list[Transaction]:
        statement = select(Transaction).order_by(
            Transaction.occurred_on.desc(),
            Transaction.id.desc()
        )

        return list(self._session.scalars(statement).all())
