from collections.abc import Iterator
from pathlib import Path

import pytest

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.category import CategoryType
from pynance.repositories.category_repository import CategoryRepository
from pynance.services.category_service import CategoryService


@pytest.fixture
def category_service(tmp_path: Path) -> Iterator[CategoryService]:
    database_url = f"sqlite:///{tmp_path / 'pynance_test.db'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            yield CategoryService(CategoryRepository(session))
    finally:
        engine.dispose()


def test_category_service_creates_category(
    category_service: CategoryService,
) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    assert category.id is not None
    assert category.name == "Food"
    assert category.category_type == CategoryType.EXPENSE


def test_category_service_strips_category_name(
    category_service: CategoryService,
) -> None:
    category = category_service.create_category(
        name="  Food  ",
        category_type=CategoryType.EXPENSE,
    )

    assert category.name == "Food"


def test_category_service_rejects_empty_category_name(
    category_service: CategoryService,
) -> None:
    with pytest.raises(ValueError, match="Category name cannot be empty"):
        category_service.create_category(
            name="   ",
            category_type=CategoryType.EXPENSE,
        )


def test_category_service_rejects_duplicate_category_name(
    category_service: CategoryService,
) -> None:
    category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    with pytest.raises(ValueError, match="Category name already exists"):
        category_service.create_category(
            name="Food",
            category_type=CategoryType.INCOME,
        )


def test_category_service_lists_categories(category_service: CategoryService) -> None:
    category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )
    category_service.create_category(
        name="Salary",
        category_type=CategoryType.INCOME,
    )

    categories = category_service.list_categories()

    assert [category.name for category in categories] == ["Food", "Salary"]


def test_category_service_gets_category(category_service: CategoryService) -> None:
    created_category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    category = category_service.get_category(created_category.id)

    assert category.name == "Food"


def test_category_service_rejects_missing_category(
    category_service: CategoryService,
) -> None:
    with pytest.raises(ValueError, match="Category not found"):
        category_service.get_category(999)


def test_category_service_updates_category(category_service: CategoryService) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    updated_category = category_service.update_category(
        category.id,
        name="  Groceries  ",
        category_type=CategoryType.EXPENSE,
    )

    assert updated_category.name == "Groceries"
    assert updated_category.category_type == CategoryType.EXPENSE


def test_category_service_rejects_update_without_fields(
    category_service: CategoryService,
) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    with pytest.raises(ValueError, match="At least one field must be provided"):
        category_service.update_category(category.id)


def test_category_service_rejects_empty_updated_category_name(
    category_service: CategoryService,
) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    with pytest.raises(ValueError, match="Category name cannot be empty"):
        category_service.update_category(category.id, name="   ")


def test_category_service_rejects_duplicate_updated_category_name(
    category_service: CategoryService,
) -> None:
    category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )
    salary_category = category_service.create_category(
        name="Salary",
        category_type=CategoryType.INCOME,
    )

    with pytest.raises(ValueError, match="Category name already exists"):
        category_service.update_category(salary_category.id, name="Food")


def test_category_service_allows_unchanged_updated_category_name(
    category_service: CategoryService,
) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    updated_category = category_service.update_category(category.id, name="Food")

    assert updated_category.name == "Food"


def test_category_service_deletes_category(category_service: CategoryService) -> None:
    category = category_service.create_category(
        name="Food",
        category_type=CategoryType.EXPENSE,
    )

    category_service.delete_category(category.id)

    with pytest.raises(ValueError, match="Category not found"):
        category_service.get_category(category.id)
