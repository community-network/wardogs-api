import datetime

from database.connection import Base
from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class Unlock(Base):
    __tablename__ = "unlocks"
    account_id: Mapped[int] = mapped_column(BigInteger, index=True)

    node_id: Mapped[int] = mapped_column(BigInteger)
    level: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
