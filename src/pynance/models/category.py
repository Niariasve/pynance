from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pynance.database import Base


class CategoryType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    __tablename__ = "category"

    __table_args__ = CheckConstraint(
        "category_type IN ('income', 'expense')", name="check_category_type"
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"Category(id={self.id!r}), "
            f"name={self.name!r}, "
            f"category_type={self.category_type!r}"
        )
