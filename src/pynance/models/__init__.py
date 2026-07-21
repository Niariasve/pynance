# models/__init__.py
def import_models() -> None:
    from pynance.models.account import Account

    _ = Account