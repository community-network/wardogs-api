from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dto import DiscordUser


async def upsert(
    session: AsyncSession,
    account_id: int,
    discord_id: int,
    display_name: str | None,
):
    data = {
        "account_id": account_id,
        "discord_id": discord_id,
        "display_name": display_name,
    }
    stmt = insert(DiscordUser).values(data)
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=[DiscordUser.account_id],
        set_={k: v for (k, v) in data.items() if k != "created_at"},
    )
    try:
        result = await session.execute(do_update_stmt)
        await session.commit()
        return result.scalar_one()
    except IntegrityError:
        pass
