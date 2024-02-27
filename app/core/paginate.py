# from __future__ import annotations
#
# from dataclasses import asdict
# from typing import Sequence, TypeVar, Generic
#
# from fastapi_pagination.bases import AbstractParams, AbstractPage, RawParams
# from fastapi_pagination import LimitOffsetParams
# from pydantic.types import conint
# from pydantic import BaseModel
# from fastapi import Query
#
# T = TypeVar("T")
#
#
# class CustomParams(BaseModel, AbstractParams):
#     """
#     Custom params.
#     """
#
#     limit: int = Query(50, ge=1, le=500, description="Page size limit")
#     offset: int = Query(0, ge=0, description="Page offset")
#
#     def to_raw_params(self) -> RawParams:
#         return RawParams(
#             limit=self.limit,
#             offset=self.offset,
#         )
#
#
# class CustomPage(AbstractPage[T], Generic[T]):
#     """
#     Custom paginate page with the general field.
#     """
#
#     items: Sequence[T]
#     general: dict
#     total: int
#     limit: conint(ge=1)  # type: ignore
#     offset: conint(ge=0)  # type: ignore
#
#     __params_type__ = CustomParams
#
#     @classmethod
#     def create(
#         cls, items: Sequence[T], total: int, params: AbstractParams, **kwargs
#     ) -> CustomPage[T]:
#         return cls(
#             total=total, items=items, general=kwargs, **asdict(params.to_raw_params())
#         )
#
#
# Page = CustomPage
# Params = LimitOffsetParams
#
# __all__ = [
#     "Page",
#     "Params",
#     "CustomPage",
#     "LimitOffsetParams",
# ]
