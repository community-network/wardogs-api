import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class WardogAccount(Base):
    __tablename__ = "wardog_accounts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    steam_id: Mapped[str]
    wardogs_player_id: Mapped[str | None] = mapped_column(nullable=True)
    social_id: Mapped[str | None] = mapped_column(nullable=True)

    display_name: Mapped[str | None] = mapped_column(nullable=True)
    discriminator: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
