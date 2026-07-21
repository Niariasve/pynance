from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from pynance.database import create_engine_from_url, create_session_factory, init_db
from pynance.models.category import Category, CategoryType
from pynance.repositories.category_repository import CategoryRepository


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    database_url = f"sqlite:///{tmp_path / 'pynance_test.db'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)

    try:
        yield create_session_factory(engine)
    finally:
        engine.dispose()


def test_category_repository_adds_category(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)

        category = repository.add(
            Category(name="Food", category_type=CategoryType.EXPENSE)
        )

        assert category.id is not None
        assert category.name == "Food"


def test_category_repository_lists_all_categories(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)
        repository.add(Category(name="Food", category_type=CategoryType.EXPENSE))
        repository.add(Category(name="Salary", category_type=CategoryType.INCOME))

        categories = repository.list_all()

        assert [category.name for category in categories] == ["Food", "Salary"]


def test_category_repository_gets_category_by_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)
        created_category = repository.add(
            Category(name="Food", category_type=CategoryType.EXPENSE)
        )

        category = repository.get_by_id(created_category.id)

        assert category is not None
        assert category.name == "Food"


def test_category_repository_gets_category_by_name(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)
        repository.add(Category(name="Food", category_type=CategoryType.EXPENSE))

        category = repository.get_by_name("Food")

        assert category is not None
        assert category.name == "Food"


def test_category_repository_deletes_category(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)
        category = repository.add(
            Category(name="Food", category_type=CategoryType.EXPENSE)
        )

        repository.delete(category)

        assert repository.get_by_id(category.id) is None


def test_category_repository_updates_category(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = CategoryRepository(session)
        category = repository.add(
            Category(name="Food", category_type=CategoryType.EXPENSE)
        )

        category.name = "Groceries"
        category.category_type = CategoryType.EXPENSE
        updated_category = repository.update(category)

        assert updated_category.name == "Groceries"
        assert updated_category.category_type == CategoryType.EXPENSE

        persisted_category = repository.get_by_id(category.id)
        assert persisted_category is not None
        assert persisted_category.name == "Groceries"
