from datetime import date, datetime
from decimal import Decimal
from typing import Any, Type

from aiogram.fsm.state import State
from sqlalchemy import BigInteger, delete, desc, func, select, update, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from tire_bot.database.models import (
    AdminDB,
    Base,
    DiameterDB,
    MainDB,
    PayDB,
    PriceDB,
    ServiceDB,
    async_session,
)


def connection(function):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await function(session, *args, **kwargs)

    return inner


@connection
async def get_available(session: AsyncSession, dbname: Type[Base]) -> ScalarResult[Any]:
    return await session.scalars(select(dbname))


@connection
async def check_available(session: AsyncSession, dbname: Type[Base], req: str) -> bool:
    model = await session.scalar(select(dbname).where(dbname.name == req))
    try:
        result = model.name
        return True
    except Exception as e:
        print(e)
        return False


@connection
async def approximate_price(session: AsyncSession, service_name: str) -> int:
    result = await session.scalar(
        select(PriceDB).where(PriceDB.service == service_name)
    )
    return result.R17


@connection
async def to_main_bd(
    session: AsyncSession,
    user_name,
    tg_id,
    diameter,
    service,
    additional_service,
    payment_type,
    discount,
    price,
) -> None:
    sale = MainDB(
        user_name=user_name,
        tg_id=tg_id,
        created_at=date.today(),
        diameter=diameter,
        service=service,
        additional_service=additional_service,
        payment_type=payment_type,
        discount=discount,
        price=price,
    )
    session.add(sale)
    await session.commit()


@connection
async def to_pay_bd(
    session: AsyncSession, tg_id, user_name, category, payer, object_, price
) -> None:
    pay = PayDB(
        user_name=user_name,
        tg_id=tg_id,
        created_at=date.today(),
        category=category,
        object=object_,
        payer=payer,
        price=price,
    )
    session.add(pay)
    await session.commit()


@connection
async def season_total(session: AsyncSession) -> int:
    result = await session.scalar(select(func.sum(MainDB.price)))
    return result


@connection
async def day_total(session: AsyncSession) -> int:
    result = await session.scalar(
        select(func.sum(MainDB.price)).where(MainDB.created_at == func.current_date())
    )
    return result


@connection
async def admin_list(session: AsyncSession):
    result = await session.scalars(select(AdminDB.tg_id))
    return result.all()
