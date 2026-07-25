from pynance.models.category import Category, CategoryType
from pynance.repositories.category_repository import CategoryRepository
from pynance.services.named_entity import clean_required_name, ensure_unique_name


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def create_category(self, *, name: str, category_type: CategoryType) -> Category:
        clean_name = clean_required_name(name, "Category")
        existing_category = self._repository.get_by_name(clean_name)
        ensure_unique_name(existing_category, "Category")

        category = Category(name=clean_name, category_type=category_type)

        return self._repository.add(category)

    def list_categories(self) -> list[Category]:
        return self._repository.list_all()

    def get_category(self, category_id: int) -> Category:
        category = self._repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")

        return category

    def update_category(
        self,
        category_id: int,
        *,
        name: str | None = None,
        category_type: CategoryType | None = None,
    ) -> Category:
        if name is None and category_type is None:
            raise ValueError("At least one field must be provided")

        category = self.get_category(category_id)

        if name is not None:
            clean_name = clean_required_name(name, "Category")
            existing_category = self._repository.get_by_name(clean_name)
            ensure_unique_name(existing_category, "Category", current_id=category_id)

            category.name = clean_name

        if category_type is not None:
            category.category_type = category_type

        return self._repository.update(category)

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        self._repository.delete(category)
