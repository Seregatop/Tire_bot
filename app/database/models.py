from sqlalchemy import ForeignKey, String, BigInteger, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime

import asyncio

from config import DB_URL

engine = create_async_engine(url=DB_URL,
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DiameterDB(Base):
    __tablename__ = 'diameters'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(4))


class ServiceDB(Base):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class AddServiceDB(Base):
    __tablename__ = 'additional_services'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class PaymentDB(Base):
    __tablename__ = 'payment_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class DiscountDB(Base):
    __tablename__ = 'discounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class PriceDB(Base):
    __tablename__ = 'prices'

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(String(15)) # 1пропуск и как-то сделать список всех услуг автоматом
    R13: Mapped[str] = mapped_column(String(15))
    R14: Mapped[str] = mapped_column(String(15))
    R15: Mapped[str] = mapped_column(String(15))
    R16: Mapped[str] = mapped_column(String(15))
    R17: Mapped[str] = mapped_column(String(15))
    R18: Mapped[str] = mapped_column(String(15))
    R19: Mapped[str] = mapped_column(String(15))
    R20: Mapped[str] = mapped_column(String(15))
    R21: Mapped[str] = mapped_column(String(15))
    R22: Mapped[str] = mapped_column(String(15))


class MainDB(Base):
    __tablename__ = 'main'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(15))
    diameter: Mapped[str] = mapped_column(String(15))
    service: Mapped[str] = mapped_column(String(15))
    additional_service: Mapped[str] = mapped_column(String(15))
    payment_type: Mapped[str] = mapped_column(String(15))
    discount: Mapped[str] = mapped_column(String(15))
    price: Mapped[str] = mapped_column(String(15))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# async def test():
#     async with async_session() as session:
#         model = await session.scalars(select(DiameterDB).where(DiameterDB.name == 'R13'))
#         print(model.all())
