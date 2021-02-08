# -*- coding: utf-8 -*-
__author__ = 'wuhai'
import json
import datetime

from django.core.serializers import serialize


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, str):
            return obj
        else:
            return json.JSONEncoder.default(self, obj)


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattribute__ = dict.__getitem__


# 递归把dict转换成obj对象[兼容obj.属性和obj[属性]]
def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    d = Dict()
    for k, v in dictObj.items():
        d[k] = dict_to_object(v)
