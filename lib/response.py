# coding:utf-8
from rest_framework.response import Response as OrgResponse


class Response(OrgResponse):
    def __init__(self, data=None, status=None, template_name=None, headers=None,
                 exception=False, content_type=None, code=0, msg="Success"):
        if data is None:
            data = {}
        super(Response, self).__init__(data, status, template_name, headers,
                                       exception, content_type)

        self.data = {
            "code": code,
            "msg": msg,
            "data": data
        }
