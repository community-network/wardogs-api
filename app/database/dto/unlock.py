import datetime

from database.connection import Base
from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column


class Unlock(Base):
    __tablename__ = "unlocks"
    account_id: Mapped[int] = mapped_column(
        ForeignKey("wardog_accounts.id", ondelete="cascade"),
        nullable=False,
        primary_key=True,
    )
    node_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    level: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
