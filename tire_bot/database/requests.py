from datetime import date, datetime
from decimal import Decimal
from typing import Any, Type

from aiogram.fsm.state import State
from sqlalchemy import (BigInteger, ScalarResult, delete, desc, func, select,
                        update)
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from tire_bot.database.models import (AdminDB, Base, DiameterDB, MainDB, PayDB,
                                      PriceDB, ServiceDB)


class DatabaseHandler:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(url=db_url, echo=True)
        self.session = async_sessionmaker(self.engine)()

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_available(self, dbname: Type[Base]) -> ScalarResult[Any]:
        """Возвращает список доступных значений из заданной таблицы."""
        return await self.session.scalars(select(dbname))

    async def check_available(self, dbname: Type[Base], req: str) -> bool:
        """Функция проверяет наличие значения в таблице"""
        model = await self.session.scalar(select(dbname).where(dbname.name == req))
        try:
            result = model.name
            return True
        except Exception as e:
            print(e)
            return False

    async def approximate_price(self, service_name: str, diameter: str) -> int:
        """Возвращает цену"""
        result = await self.session.scalar(
            select(PriceDB).where(PriceDB.service == service_name)
        )
        return getattr(result, diameter)

    async def to_main_bd(
        self,
        user_name,
        tg_id,
        diameter,
        service,
        additional_service,
        payment_type,
        discount,
        price,
    ) -> None:
        """ "Запись продажи"""
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
        self.session.add(sale)
        await self.session.commit()

    async def to_pay_bd(
        self, tg_id, user_name, category, payer, object_, price
    ) -> None:
        """Запись расхода"""
        pay = PayDB(
            user_name=user_name,
            tg_id=tg_id,
            created_at=date.today(),
            category=category,
            object=object_,
            payer=payer,
            price=price,
        )
        self.session.add(pay)
        await self.session.commit()

    async def season_total(self) -> int:
        """Возвращает оборот за все время"""
        result = await self.session.scalar(select(func.sum(MainDB.price)))
        return result

    async def day_total(self) -> int:
        """Возвращает оборот за сегодня"""
        result = await self.session.scalar(
            select(func.sum(MainDB.price)).where(
                MainDB.created_at == func.current_date()
            )
        )
        return result

    async def admin_list(self):
        """Возвращает список телеграм ID администраторов"""
        result = await self.session.scalars(select(AdminDB.tg_id))
        return result.all()
