from database.dto.wardogs_account import WardogAccount
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_create(
    session: AsyncSession,
    steam_id: str,
    wardogs_player_id: str | None = None,
    social_id: str | None = None,
    display_name: str | None = None,
    discriminator: str | None = None,
) -> WardogAccount | None:
    stmt = select(WardogAccount).filter(WardogAccount.steam_id == steam_id).limit(1)
    result = await session.execute(stmt)
    res = result.scalar_one_or_none()
    if res is None:
        channel = {
            "steam_id": steam_id,
            "wardogs_player_id": wardogs_player_id,
            "social_id": social_id,
            "display_name": display_name,
            "discriminator": discriminator,
        }
        stmt = insert(WardogAccount).values(channel).returning(WardogAccount)
        try:
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()
        except IntegrityError:
            pass
