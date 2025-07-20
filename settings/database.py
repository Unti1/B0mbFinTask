import asyncio
from datetime import datetime
import sys
from typing import Annotated, List, Self
import uuid

from settings.config import moscow_tz
from sqlalchemy import DateTime, String, select, update
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from settings.config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# connection decorator
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper


class Base(DeclarativeBase, AsyncAttrs):
    """Шаблонный класс для создания и взаимодействия с моделями класса"""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.now(moscow_tz).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.now(moscow_tz).replace(tzinfo=None),
        onupdate=lambda: datetime.now(moscow_tz).replace(tzinfo=None),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    @classmethod
    @connection
    async def get(cls, session: AsyncSession = None, **creterias) -> None | Self:
        """Возвращает искомый объет базы данных по переданным creterias

        Args:
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.
        Returns:
            None|Self: Объект или None
        """
        query = select(cls).filter_by(**creterias)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    @classmethod
    @connection
    async def get_all_by_creterias(
        cls, session: AsyncSession = None, limit: int | None = None, **creterias
    ) -> list[Self]:
        """Возвращает искомые объеты базы данных по переданным creterias

        Args:
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.
            limit (int|None): Ограничение по выводу информации. Defaults to None
        Returns:
            list[Self]: Список найденных объектов
        """
        if limit:
            query = select(cls).filter_by(**creterias).limit(limit)
        else:
            query = select(cls).filter_by(**creterias)
        rows = await session.execute(query)
        return rows.scalars().all()

    @classmethod
    @connection
    async def get_all(
        cls, session: AsyncSession = None, limit: int | None = None
    ) -> list[Self]:
        """Выводит все строки таблицы

        Args:
            limit (int|None): Ограничение по выводу информации. Defaults to None
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.

        Returns:
            list[Self]: _description_
        """
        if limit:
            query = select(cls).limit(limit)
        else:
            query = select(cls)
        rows = await session.execute(query)
        return rows.scalars().all()

    @classmethod
    @connection
    async def create(
        cls,
        session: AsyncSession = None,
        **data,
    ) -> Self:
        """Создание новой строки в БД, по переданным data

        Args:
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.

        Returns:
            Self
        """
        new_row = cls(**data)
        session.add(new_row)
        await session.commit()
        return new_row

    @classmethod
    @connection
    async def create_many(
        cls,
        datas: list[dict],
        session: AsyncSession = None,
    ) -> list[Self]:
        """Создает несколько объектов за раз

        Args:
            datas (list[dict]): Список данных для каждой строки БД
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.

        Returns:
            list[Self]
        """
        new_rows = [cls(**data) for data in datas]
        session.add_all(new_rows)
        await session.commit()
        return new_rows

    @classmethod
    @connection
    async def update(cls, id: int, session: AsyncSession = None, **data) -> Self:
        """Обновление данных для одного объекта

        Args:
            id (int): Идентификатор объекта
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.

        Raises:
            ValueError: если нет колонки или строки с переданным id

        Returns:
            Self
        """
        query = select(cls).where(cls.id == id).with_for_update(of=cls)
        rows = await session.execute(query)
        concrete_row = rows.scalar_one_or_none()

        if not concrete_row:
            raise ValueError(
                f"Данные с таким id в таблице {cls.__tablename__} не найдены"
            )

        for key, value in data.items():
            if key not in concrete_row.__dict__:
                raise ValueError(f'Колонки "{key}" нету в таблице {cls.__tablename__}')
            if getattr(concrete_row, key) != value:
                setattr(concrete_row, key, value)

        await session.commit()
        return concrete_row

    @classmethod
    @connection
    async def update_field(
        cls, id: int, field: str, value: any, session: AsyncSession = None
    ) -> bool:
        """Обновление одного поля для объекта без блокировки связанных таблиц

        Args:
            id (int): Идентификатор объекта
            field (str): Имя поля для обновления
            value (any): Новое значение
            session (Session, optional): Сессия запроса. Defaults to None.

        Returns:
            bool: True если обновление успешно, False если объект не найден
        """
        stmt = update(cls).where(cls.id == id).values(**{field: value})
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    @classmethod
    @connection
    async def delete(
        cls,
        id: int,
        session: AsyncSession = None,
    ) -> bool:
        """Удаление строки данных

        Args:
            id (int): Идентификатор объекта(по полю id)
            session (Session, optional): Сессия запроса(подставляется автоматически). Defaults to None.

        Returns:
            bool
        """
        query = select(cls).where(cls.id == id)
        rows = await session.execute(query)
        print(rows.scalars())
        row = rows.unique().scalar_one_or_none()
        if row:
            await session.delete(row)
            await session.commit()
            return True
        return False


# Annotated types
array_or_none_an = Annotated[List[str] | None, mapped_column(ARRAY(String))]
