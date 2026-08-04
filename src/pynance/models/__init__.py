# models/__init__.py
def import_models() -> None:
    from pynance.models.account import Account
    from pynance.models.category import Category
    from pynance.models.transaction import Transaction

    _ = Account, Category, Transaction
