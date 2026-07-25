from typing import Protocol


class HasId(Protocol):
    @property
    def id(self) -> int: ...


def clean_required_name(name: str, entity_label: str) -> str:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError(f"{entity_label} name cannot be empty")

    return clean_name


def ensure_unique_name(
    existing_entity: HasId | None,
    entity_label: str,
    *,
    current_id: int | None = None,
) -> None:
    if existing_entity is None:
        return

    if current_id is not None and existing_entity.id == current_id:
        return

    raise ValueError(f"{entity_label} name already exists")
