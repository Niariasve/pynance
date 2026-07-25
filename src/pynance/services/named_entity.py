from typing import Protocol

from sqlalchemy.orm import Mapped


class NamedEntity(Protocol):
    id: Mapped[int]


class NamedEntityRepository(Protocol):
    def get_by_name(self, name: str) -> NamedEntity | None: ...


def clean_required_name(name: str, entity_label: str) -> str:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError(f"{entity_label} name cannot be empty")

    return clean_name


def ensure_unique_name(
    repository: NamedEntityRepository,
    clean_name: str,
    entity_label: str,
    *,
    current_id: int | None = None,
) -> None:
    existing_entity = repository.get_by_name(clean_name)

    if existing_entity is None:
        return

    if current_id is not None and existing_entity.id == current_id:
        return

    raise ValueError(f"{entity_label} name already exists")
