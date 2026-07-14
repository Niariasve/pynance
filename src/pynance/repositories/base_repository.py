from sqlalchemy import select
from sqlalchemy.orm import Session


class BaseRepository[ModelT]:
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    def add(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> ModelT | None:
        return self._session.get(self._model, entity_id)

    def list_all(self) -> list[ModelT]:
        return list(self._session.scalars(select(self._model)).all())

    def delete(self, entity: ModelT) -> None:
        self._session.delete(entity)
        self._session.commit()
