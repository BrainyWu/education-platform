# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from datetime import datetime

from django.core.cache import cache
from rest_framework_extensions.key_constructor.bits import KeyBitBase, ListSqlQueryKeyBit, PaginationKeyBit, \
    RetrieveSqlQueryKeyBit, UniqueMethodIdKeyBit
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


class UpdatedAtKeyBit(KeyBitBase):

    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        lookup_value = view_instance.kwargs[view_instance.lookup_field]

        key = ':'.join([
            "ObjectUpdatedAt",
            view_instance.__module__,
            view_instance.get_queryset().model.__name__,
            lookup_value,
        ])

        value = cache.get(key, None)
        if not value:
            value = datetime.utcnow()
            cache.set(key, value=value)
        return str(value)


class ListKeyConstructor(KeyConstructor):
    unique_method_id = UniqueMethodIdKeyBit()
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()


class ObjectKeyConstructor(KeyConstructor):
    unique_method_id = UniqueMethodIdKeyBit()
    retrieve_sql = RetrieveSqlQueryKeyBit()
    # updated_at = UpdatedAtKeyBit()
