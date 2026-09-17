from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.wardogs_models import UnlockInfo
from app.database.dto import Unlock


async def get(session: AsyncSession, account_id: int) -> list[UnlockInfo]:
    stmt = select(Unlock).filter(Unlock.account_id == account_id)
    res = (await session.execute(stmt)).scalars().all()
    return [UnlockInfo(str(item.node_id), item.level) for item in res]


async def upsert(
    session: AsyncSession,
    account_id: int,
    unlock: UnlockInfo,
):
    data = {"account_id": account_id, "node_id": unlock.node_id, "level": unlock.level}
    stmt = insert(Unlock).values(data)
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=[Unlock.account_id, Unlock.node_id],
        set_={k: v for (k, v) in data.items() if k != "created_at"},
    )

    try:
        result = await session.execute(do_update_stmt)
        await session.commit()
        return result.scalar_one()
    except IntegrityError:
        pass
