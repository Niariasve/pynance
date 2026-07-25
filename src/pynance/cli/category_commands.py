from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pynance.cli.service_runner import run_service_operation
from pynance.models.category import Category, CategoryType
from pynance.repositories.category_repository import CategoryRepository
from pynance.services.category_service import CategoryService

category_app = typer.Typer()

console = Console()


def _categories_table(title: str) -> Table:
    table = Table(title=title)

    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Created At")
    table.add_column("Updated At")

    return table


def _add_category_row(table: Table, category: Category) -> None:
    table.add_row(
        str(category.id),
        category.name,
        category.category_type,
        f"{category.created_at.isoformat}",
        f"{category.updated_at.isoformat}",
    )


@category_app.command()
def create(
    name: Annotated[str, typer.Option()],
    category_type: Annotated[CategoryType, typer.Option("--type")],
) -> None:
    category = run_service_operation(
        CategoryRepository,
        CategoryService,
        lambda service: service.create_category(name=name, category_type=category_type),
    )

    typer.echo(f"Category created ({category.id}): {category.name}")


@category_app.command("list")
def list_categories() -> None:
    categories = run_service_operation(
        CategoryRepository,
        CategoryService,
        lambda service: service.list_categories(),
    )

    table = _categories_table("Categories")

    for category in categories:
        _add_category_row(table, category)

    console.print(table)


@category_app.command()
def show(category_id: Annotated[int, typer.Argument()]) -> None:
    category = run_service_operation(
        CategoryRepository,
        CategoryService,
        lambda service: service.get_category(category_id),
    )

    table = _categories_table("Category")
    _add_category_row(table, category)
    console.print(table)


@category_app.command()
def update(
    category_id: Annotated[int, typer.Argument()],
    name: Annotated[str | None, typer.Option()] = None,
    category_type: Annotated[CategoryType | None, typer.Option("--type")] = None,
) -> None:
    category = run_service_operation(
        CategoryRepository,
        CategoryService,
        lambda service: service.update_category(
            category_id,
            name=name,
            category_type=category_type,
        ),
    )

    typer.echo(f"Category updated ({category.id}): {category.name}")


@category_app.command()
def delete(category_id: Annotated[int, typer.Argument()]) -> None:
    run_service_operation(
        CategoryRepository,
        CategoryService,
        lambda service: service.delete_category(category_id),
    )

    typer.echo(f"Category deleted {category_id}")
