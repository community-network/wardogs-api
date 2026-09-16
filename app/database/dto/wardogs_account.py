import datetime

from database.connection import Base
from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class WardogAccount(Base):
    __tablename__ = "wardog_accounts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    steam_id: Mapped[str]
    wardogs_player_id: Mapped[str]
    social_id: Mapped[str]

    display_name: Mapped[str]
    discriminator: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
