from datetime import datetime, timezone
from typing import Any, Sequence, Type, TypeVar, Optional

import sqlalchemy as sa
from sqlalchemy import delete, func, insert, Row, RowMapping, Select, select, update, Enum, String, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.dml import ReturningDelete
from sqlalchemy.sql.functions import current_timestamp

from app.constants.messages import ErrorMessages
from app.constants.sql_base_op import SqlBasicOp
from app.utils.custom_exception import CustomException
from app.utils.string_helpers import StringHelper

MODEL = TypeVar("MODEL", bound="BaseDbModel")  # bound="xxx" xxx must be class name


class BaseDbModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[sa.Uuid] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=sa.text("gen_random_uuid()"),
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=current_timestamp(),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    def update_orm(self: Type[MODEL], data: dict):
        for key, item in data.items():
            setattr(self, key, item)

    @classmethod
    async def create(cls: Type[MODEL], session: AsyncSession, values: dict, in_transaction=True) -> Type[MODEL]:
        query = insert(cls).values(**values).returning(cls)
        result = await session.execute(query)
        if not in_transaction:
            await session.commit()
        return result.scalar_one()

    @classmethod
    async def update(cls: Type[MODEL], session: AsyncSession, values: dict, condition,
                     in_transaction=True) -> Type[MODEL]:
        query = update(cls).where(condition).values(**values).returning(cls)
        result = await session.execute(query)
        if not in_transaction:
            await session.commit()
        return result.scalar_one()

    @classmethod
    async def insert_multi(cls: Type[MODEL], session: AsyncSession, list_obj, in_transaction=True):
        session.add_all(list_obj)
        if not in_transaction:
            await session.commit()

    @classmethod
    async def generate_op_sql(cls: Type[MODEL], column, value, op, eq_w_case_insensitive=False):
        if isinstance(column, str):
            column = getattr(cls, column, None)
        if not column:
            raise CustomException(400, message='[{}] is not column in table [{}]'.format(column, cls.__table__))
        try:
            attr = list(filter(lambda e: hasattr(column, e % op), ['%s', '%s_', '__%s__']))[0] % op
        except IndexError:
            raise CustomException(400, message='filter[{}] operator({}) invalid'.format(column, op))
        if attr == 'like' or attr == 'ilike':
            search_value = StringHelper.escape_special_character_in_like_filter(value=value)
            value = search_value if eq_w_case_insensitive else "%" + search_value + "%"
        filter_obj = getattr(column, attr)(value)
        if filter_obj is NotImplemented:
            raise CustomException(message='Can\'t generate filter from column {}'.format(column))
        return filter_obj

    @classmethod
    async def get_by_column(cls: Type[MODEL], session: AsyncSession, column, value, op=SqlBasicOp.EQ.value,
                            is_many=False, options=None) -> Any | Type[MODEL]:
        filter_obj = await cls.generate_op_sql(column, value, op)
        query = select(cls).where(filter_obj)
        if options:
            query.options(options)
        result = await session.execute(query)
        if is_many:
            return result.scalars().all()
        else:
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_per_column(cls: Type[MODEL], session: AsyncSession, column, order=None,
                                 with_primary_key=True) -> Sequence[Row | RowMapping | Any]:
        if isinstance(column, str):
            column = getattr(cls, column, None)
        if with_primary_key:
            query = select(cls.__table__.primary_key, column).distinct()
        else:
            query = select(column).distinct()
        if order:
            query = query.order_by(order)
        else:
            query = query.order_by(column)
        res = await session.scalars(query)
        return res.all()

    @classmethod
    async def delete_by_column(cls: Type[MODEL], session: AsyncSession, column, value, op=SqlBasicOp.EQ.value,
                               in_transaction=True) -> ReturningDelete[Any]:
        filter_obj = await cls.generate_op_sql(column, value, op)
        statement = delete(cls).where(filter_obj).returning()
        result = await session.execute(statement)
        if not in_transaction:
            await session.commit()
        return result.rowcount

    @classmethod
    async def count(cls: Type[MODEL], session: AsyncSession, stmt: Select) -> int:
        return (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()

    @classmethod
    def generate_filter_query(cls, query, condition, key, value):
        column = condition.get(key)
        if column and value is not None:
            sub_query = column.get('sub_query')
            if isinstance(sub_query, str):
                sub_query = getattr(cls, column.get('sub_query', ''))
            query = cls.create_query_search(query=query, key=column.get('column'), value=value, sub_query=sub_query,
                                            expect_value=column.get('expect_value'), join_on=column.get('on'),
                                            table_model=column.get('table'), operator=column.get('operator'))
        return query

    @classmethod
    def create_query_search(cls, query, key, value, operator='eq', table_model=None, expect_value=None, join_on=None,
                            sub_query=None, in_json_field=None, search_equal_case_insensitive=False):
        if sub_query is None:
            if table_model is None:
                column = getattr(cls, key, None)
            else:
                if isinstance(table_model, str):
                    table_model = StringHelper.str_to_models(table_model)
                if in_json_field is None:
                    tables_from = cls.get_list_table_in_from_clause_in_query(query)
                    if isinstance(key, str):
                        column = getattr(table_model, key, None)
                    else:
                        column = key
                    if table_model not in cls.get_list_table_joined_in_query(query) \
                            and (tables_from and table_model not in tables_from) \
                            and table_model.__tablename__ != cls.__tablename__:
                        if join_on is not None:
                            query = query.join(table_model, join_on)
                        else:
                            query = query.join(table_model)
                else:
                    column = in_json_field
            if expect_value and value not in expect_value:
                raise CustomException(400, payload='{} has value invalid'.format(key))
        else:
            column = sub_query.c[key]
        try:
            attr = list(filter(lambda e: hasattr(column, e % operator), ['%s', '%s_', '__%s__']))[0] % operator
        except IndexError:
            raise CustomException(400, payload='filter[{}] operator({}) invalid'.format(key, operator))
        if attr == 'like' or attr == 'ilike':
            search_value = StringHelper.escape_special_character_in_like_filter(value=value)
            value = search_value if search_equal_case_insensitive else "%" + search_value + "%"
        filter_obj = getattr(column, attr)(value)
        if filter_obj is not NotImplemented:
            query = query.filter(filter_obj)
        return query

    @classmethod
    def create_query_sort(cls, query, column, direction='asc', null_if_empty=True):
        if isinstance(column, str):
            list_column = query.column_descriptions
            column_dict = next((item for item in list_column if item.get('name') == column), None)
            if not column_dict:
                raise CustomException(500, ErrorMessages.SORT_COLUMN_NOT_IN_SELECT)
            column = column_dict.get('expr')
        if null_if_empty and not isinstance(column.type, Enum) and isinstance(column.type, String):
            column = func.nullif(column, "")
        if direction == 'desc':
            query = query.order_by(desc(column))
        if direction == 'asc':
            query = query.order_by(column)
        return query

    @classmethod
    def get_list_table_in_from_clause_in_query(cls, query):
        return [mapper.entity_namespace for mapper in query.selectable.columns_clause_froms if
                isinstance(mapper.entity_namespace, BaseDbModel)]

    @classmethod
    def get_list_table_joined_in_query(cls, query):
        return [mapper[0].entity_namespace for mapper in query._legacy_setup_joins if
                isinstance(mapper[0].entity_namespace, BaseDbModel)]
