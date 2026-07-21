from sqlalchemy import select
from sqlalchemy.orm import Session

from pynance.models.category import Category
from pynance.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Category)

    def get_by_name(self, name: str) -> Category | None:
        return self._session.scalars(
            select(Category).where(Category.name == name)
        ).one_or_none()
