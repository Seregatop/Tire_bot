import asyncio
from datetime import date, datetime

from sqlalchemy import BigInteger, ForeignKey, String, func, select, text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DB_URL

engine = create_async_engine(url=DB_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DiameterDB(Base):
    __tablename__ = "diameters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(4))


class ServiceDB(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class AddServiceDB(Base):
    __tablename__ = "additional_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class PaymentDB(Base):
    __tablename__ = "payment_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class DiscountDB(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


# Таблица со списком телеграм ID администраторов
class AdminDB(Base):
    __tablename__ = "administrators"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


# Таблица с ценами
class PriceDB(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(
        String(15)
    )  # 1пропуск и как-то сделать список всех услуг автоматом
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


# Главная таблица со записями продаж
class MainDB(Base):
    __tablename__ = "main"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    created_at: Mapped[date] = mapped_column(server_default=func.current_date())
    user_name: Mapped[str] = mapped_column(String(15))
    diameter: Mapped[str] = mapped_column(String(15))
    service: Mapped[str] = mapped_column(String(15))
    additional_service: Mapped[str] = mapped_column(String(15))
    payment_type: Mapped[str] = mapped_column(String(15))
    discount: Mapped[str] = mapped_column(String(15))
    price: Mapped[str] = mapped_column(String(15))


class CategoryDB(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class PayerDB(Base):
    __tablename__ = "payers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))


class PayDB(Base):
    __tablename__ = "pay"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    created_at: Mapped[date] = mapped_column(server_default=func.current_date())
    user_name: Mapped[str] = mapped_column(String(15))
    category: Mapped[str] = mapped_column(String(15))
    object: Mapped[str] = mapped_column(String(15))
    payer: Mapped[str] = mapped_column(String(15))
    price: Mapped[str] = mapped_column(String(15))


async def db_init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
