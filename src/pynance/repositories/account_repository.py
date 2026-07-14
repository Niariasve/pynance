from sqlalchemy import select
from sqlalchemy.orm import Session

from pynance.models.account import Account
from pynance.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Account)

    def get_by_name(self, name: str) -> Account | None:
        return self._session.scalars(
            select(Account).where(Account.name == name)
        ).one_or_none()
