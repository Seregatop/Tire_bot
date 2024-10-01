from sqlalchemy import BigInteger

from app.database.models import async_session
from sqlalchemy import select, update, delete, desc
from decimal import Decimal


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def get_available(session, dbname):
    return await session.scalars(select(dbname))


@connection
async def check_available(session, dbname, req):
    available = await session.scalars(select(dbname))
    print('----------------------------------------------------------')
    print(*available)
    return req in available
