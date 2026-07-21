import typer

from pynance.cli.account_commands import accounts_app
from pynance.database import (
    DATABASE_PATH,
    DATABASE_URL,
    create_engine_from_url,
    init_db,
)
from pynance.models import account as _account

app = typer.Typer()

app.add_typer(accounts_app, name="accounts")


@app.callback()
def callback() -> None:
    """Pynance personal finance CLI."""


@app.command()
def init() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine_from_url(DATABASE_URL)

    try:
        init_db(engine)
    finally:
        engine.dispose()

    typer.echo("Database initialized")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
