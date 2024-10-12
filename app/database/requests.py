from datetime import datetime, date

from sqlalchemy import BigInteger, func
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base, MainDB, AdminDB

from aiogram.fsm.state import State
from app.database.models import async_session, DiameterDB, ServiceDB, PriceDB

from decimal import Decimal


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return inner


@connection
async def get_available(session: AsyncSession, dbname):
    return await session.scalars(select(dbname))


@connection
async def check_available(session: AsyncSession, dbname: Base, req: str):
    model = await session.scalar(select(dbname).where(dbname.name == req))
    try:
        result = model.name
        return True
    except Exception as e:
        print(e)
        return False


@connection
async def approximate_price(session: AsyncSession,
                            service_name: str) -> int:
    result = await session.scalar(select(PriceDB).where(PriceDB.service == service_name))
    return result.R17


@connection
async def to_bd(session: AsyncSession, tg_id, user_name, diameter, service, additional_service, payment_type, discount,
                price):
    sale = MainDB(user_name=user_name, tg_id=tg_id, created_at=date.today(), diameter=diameter, service=service,
                  additional_service=additional_service, payment_type=payment_type, discount=discount, price=price)
    session.add(sale)
    await session.commit()


@connection
async def season_total(session: AsyncSession):
    result = await session.scalar(select(func.sum(MainDB.price)))
    return result


@connection
async def day_total(session: AsyncSession):
    result = await session.scalar(select(func.sum(MainDB.price)).where(MainDB.created_at == func.current_date()))
    return result


@connection
async def admin_list(session: AsyncSession):
    result = await session.scalars(select(AdminDB.tg_id))
    return result.all()
