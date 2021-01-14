# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, _get_error_details


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid params.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]
        self.detail = _get_error_details(detail, code)

    def __str__(self):
        return str(self.detail)


def custom_exception_handler(exc, context):
    """自定义返回"""
    response = exception_handler(exc, context)

    if response is not None:
        response.data['data'] = {}
        response.data['code'] = -1
        response.data['msg'] = {'error': str(exc)}

        if 'detail' in response.data:
            response.data['msg'] = response.data['detail']
            del response.data['detail']  # 删除detail字段
        else:
            for key in dict(response.data).keys():
                if key not in ['code', 'msg', 'data']:
                    response.data['msg'][key] = response.data[key]
                    del response.data[key]
    return response
