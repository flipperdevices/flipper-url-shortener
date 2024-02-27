# from __future__ import annotations
#
# from dataclasses import dataclass, asdict
#
# from fastapi_pagination.ext.sqlalchemy import paginate, paginate_query
# from fastapi_pagination.bases import AbstractPage
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi_pagination.api import page_type
# from fastapi_pagination import resolve_params
# from sqlalchemy import select, func
#
# paginate()
# class CustomPaginateService:
#     """
#     Custom sqlalchemy paginate service.
#     """
#
#     @staticmethod
#     async def get_pagination_params() -> dict:
#         """
#         Get dict of pagination params (limit and offset).
#         """
#         row_params = resolve_params().to_raw_params()
#         return asdict(row_params, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
#
#     @staticmethod
#     async def get_row_pagination_params() -> dataclass:
#         """
#         Get dataclass of pagination params (limit and offset).
#         """
#         return resolve_params().to_raw_params()
#
#     @staticmethod
#     async def force_page(items, total, params=None, **kwargs) -> AbstractPage:
#         """
#         Blank paginate page.
#         """
#         params = resolve_params(params)
#
#         return page_type.get().create(items, total, params, **kwargs)
#
#     @staticmethod
#     async def blank_page(params=None, **kwargs) -> AbstractPage:
#         """
#         Blank paginate page.
#         """
#         params = resolve_params(params)
#
#         return page_type.get().create([], 0, params, **kwargs)
#
#     @staticmethod
#     async def paginate_no_scalars(session: AsyncSession, query, params=None, **kwargs) -> AbstractPage:
#         """
#         Sqlalchemy paginate without items scalars() and unique() methods.
#         """
#         params = resolve_params(params)
#
#         total = await session.scalar(select(func.count()).select_from(query.subquery()))
#         items = await session.execute(paginate_query(query, params))
#
#         items = items.all()
#
#         return page_type.get().create(items, total, params, **kwargs)
#
#     @staticmethod
#     async def paginate_scalars(session: AsyncSession, query, params=None, **kwargs) -> AbstractPage:
#         """
#         Sqlalchemy paginate.
#         """
#         params = resolve_params(params)
#
#         total = await session.scalar(select(func.count()).select_from(query.subquery()))
#         items = await session.execute(paginate_query(query, params))
#
#         items = items.scalars().unique().all()
#
#         return page_type.get().create(items, total, params, **kwargs)
#
#     @staticmethod
#     async def get_pagination_result(session: AsyncSession, query, params=None, **kwargs) -> dict:
#         """
#         Sqlalchemy paginate without items scalars() and unique() methods.
#         """
#         params = resolve_params(params)
#
#         total = await session.scalar(select(func.count()).select_from(query.subquery()))
#         items = await session.execute(paginate_query(query, params))
#         items = [dict(item) for item in items.fetchall()]
#
#         return {'items': items, 'total': total, 'params': params}
