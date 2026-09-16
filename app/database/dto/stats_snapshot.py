import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class StatsSnapshot(Base):
    __tablename__ = "stats_snapshots"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("wardog_accounts.id", ondelete="cascade"), nullable=False
    )
    player_data_version: Mapped[int | None] = mapped_column(BigInteger)

    wardog_level: Mapped[int] = mapped_column(BigInteger)

    infantry_level: Mapped[int] = mapped_column(BigInteger)
    infantry_xp: Mapped[int] = mapped_column(BigInteger)

    medic_level: Mapped[int] = mapped_column(BigInteger)
    medic_xp: Mapped[int] = mapped_column(BigInteger)

    recon_level: Mapped[int] = mapped_column(BigInteger)
    recon_xp: Mapped[int] = mapped_column(BigInteger)

    support_level: Mapped[int] = mapped_column(BigInteger)
    support_xp: Mapped[int] = mapped_column(BigInteger)

    driver_level: Mapped[int] = mapped_column(BigInteger)
    driver_xp: Mapped[int] = mapped_column(BigInteger)

    pilot_level: Mapped[int] = mapped_column(BigInteger)
    pilot_xp: Mapped[int] = mapped_column(BigInteger)

    cash: Mapped[int] = mapped_column(BigInteger)
    gold: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
