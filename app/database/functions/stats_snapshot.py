from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.wardogs_models import PlayerStats
from app.database.dto.stats_snapshot import StatsSnapshot
from app.database.functions import unlocks


async def create(
    session: AsyncSession,
    account_id: int,
    stats: PlayerStats,
):
    channel = {
        "account_id": account_id,
        "player_data_version": stats.player_data_version,
        "wardog_level": stats.wardog_level,
        "infantry_level": stats.infantry.level,
        "infantry_xp": stats.infantry.level,
        "medic_level": stats.medic.level,
        "medic_xp": stats.medic.level,
        "recon_level": stats.recon.level,
        "recon_xp": stats.recon.level,
        "support_level": stats.support.level,
        "support_xp": stats.support.level,
        "driver_level": stats.driver.level,
        "driver_xp": stats.driver.level,
        "pilot_level": stats.pilot.level,
        "pilot_xp": stats.pilot.xp,
        "cash": stats.cash,
        "gold": stats.gold,
    }
    stmt = insert(StatsSnapshot).values(channel).returning(StatsSnapshot)
    result = await session.execute(stmt)
    await session.commit()

    for unlock in stats.unlocks:
        await unlocks.upsert(session, account_id, unlock)

    return result.scalar_one()
