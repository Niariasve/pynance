from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy import Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pynance.database import Base

AccountType = Literal["cash", "bank", "credit_card", "savings"]


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
