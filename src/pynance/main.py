import typer

app = typer.Typer()


@app.command()
def greet(name: str) -> None:
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False) -> None:
    if formal:
        print(f"Goodbye Mr. {name}, have a good day")
    else:
        print(f"See ya {name}!")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
