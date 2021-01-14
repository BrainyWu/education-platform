# _*_ encoding:utf-8 _*_

from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView, ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken
from datetime import datetime


class CustomJSONWebTokenAPIView(JSONWebTokenAPIView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response
        error_data = jwt_response_payload_error_handler(serializer, request)
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class CustomObtainJSONWebToken(ObtainJSONWebToken, CustomJSONWebTokenAPIView):
    pass


class CustomRefreshJSONWebToken(RefreshJSONWebToken, CustomJSONWebTokenAPIView):
    pass


class CustomVerifyJSONWebToken(VerifyJSONWebToken, CustomJSONWebTokenAPIView):
    pass


def jwt_response_payload_handler(token, user=None, request=None):
    """
    设置jwt登陆返回的格式
    """
    return {
        "msg": "success",
        "status": 200,
        "data": {
            'token': token,
            'user_id': user.id,
            'username': user.username,
        }
    }


def jwt_response_payload_error_handler(serializer, request = None):
    return {
        "msg": "用户名或者密码错误",
        "status": 400,
        "detail": serializer.errors
    }


obtain_jwt_token = CustomObtainJSONWebToken.as_view()
refresh_jwt_token = CustomRefreshJSONWebToken.as_view()
verify_jwt_token = CustomVerifyJSONWebToken.as_view()