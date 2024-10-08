from sqlalchemy import BigInteger
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base, MainDB

from aiogram.fsm.state import State
from app.database.models import async_session, DiameterDB, ServiceDB, PriceDB

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
async def check_available(session, dbname: Base, req: str):
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
async def approximate_price(session, service_name: str) -> int: # из user_data берем услугу(user_data['chosen_diameter']) и диаметр(user_data['chosen_service'])
    pass
    # x = await session.scalar(select(DiameterDB).where(DiameterDB.name == user_data['chosen_diameter']))
    y = await session.scalar(select(PriceDB).where(PriceDB.service == service_name))
    return y.R17
    # return await session.scalar(select(PriceDB).where(PriceDB.))


@connection
async def to_bd(session: AsyncSession, user_name, diameter, service, additional_service, payment_type, discount, price): # должна записывать много всего в БД
    sale = MainDB(user_name=user_name, diameter=diameter, service=service, additional_service=additional_service,
                  payment_type=payment_type, discount=discount, price=price)
    session.add(sale)
    await session.commit()

    # x = await session.scalar(select(DiameterDB).where(DiameterDB.name == user_data['chosen_diameter']))
    # y = await session.scalar(select(ServiceDB).where(ServiceDB.name == user_data['chosen_service']))
    # return await session.scalar(select(PriceDB).where(PriceDB.))