from sqlalchemy.orm import Session

from pynance.models.transaction import Transaction
from pynance.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Transaction)
