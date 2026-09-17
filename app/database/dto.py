import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class WardogAccount(Base):
    __tablename__ = "wardog_accounts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stats_snapshots: Mapped[list["StatsSnapshot"]] = relationship(
        "StatsSnapshot", back_populates="account"
    )
    unlocks: Mapped[list["Unlock"]] = relationship("Unlock", back_populates="account")
    discord_users: Mapped[list["DiscordUser"]] = relationship(
        "DiscordUser", back_populates="account"
    )

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


class Unlock(Base):
    __tablename__ = "unlocks"
    account_id: Mapped[int] = mapped_column(
        ForeignKey("wardog_accounts.id", ondelete="cascade"),
        nullable=False,
        primary_key=True,
    )
    account: Mapped["WardogAccount"] = relationship(
        "WardogAccount",
        back_populates="unlocks",
    )
    node_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    level: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DiscordUser(Base):
    __tablename__ = "discord_users"
    discord_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    display_name: Mapped[str | None] = mapped_column(nullable=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("wardog_accounts.id", ondelete="cascade"), nullable=False
    )
    account: Mapped["WardogAccount"] = relationship(
        "WardogAccount", back_populates="discord_users"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StatsSnapshot(Base):
    __tablename__ = "stats_snapshots"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("wardog_accounts.id", ondelete="cascade"), nullable=False
    )
    account: Mapped["WardogAccount"] = relationship(
        "WardogAccount",
        back_populates="stats_snapshots",
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
