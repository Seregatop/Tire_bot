from sqlalchemy import BigInteger
from aiogram.fsm.state import State

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
    model = await session.scalar(select(dbname).where(dbname.name == req))
    try:
        result = model.name
        return True
    except Exception as e:
        print(e)
        return False
    # result = await session.execute()
    # result = await session.scalars(dbname).filter(dbname.name == req).first()


@connection
async def approximate_price(session, user_data):
    return '404'
