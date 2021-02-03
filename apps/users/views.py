# _*_ encoding:utf-8 _*_
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import mixins, viewsets, status, authentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import UserRegSerializer, UserSerializer, ResetPwdSerializer, \
    ModifyPwdSerializer, EmailModifySerializer
from courses.serializers import CourseSerializer
from lib.response import Response
from lib.utils import BasePagination, get_object
from operation.models import UserCourse, UserFavorite, UserMessage
from operation.serializers import UserMessageSerializer, UserCourseSerializer
from organization.serializers import CourseOrgSerializer, TeacherSerializer
from utils.email_send import send_email

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户认证方式
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = get_object(User, username=username)
            if user.check_password(password):
                return user
        except:
            return None


class UserView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用户注册，个人信息详情, 修改个人信息
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_object(self):
        return get_object(User, self.request.user.id)

    def perform_create(self, serializer):
        # 返回user
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        # 返回token
        re_dict["token"] = jwt_encode_handler(payload)

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action != "create":
            return UserSerializer
        else:
            return UserRegSerializer

    def get_permissions(self):
        if self.action != "create":
            return [IsAuthenticated()]
        else:
            return []


class ModifyPwdView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改用户密码
    """
    serializer_class = ModifyPwdSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object(User, self.request.user.id)


class ResetPwdView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    重置密码
    """
    serializer_class = ResetPwdSerializer

    def get_object(self):
        return get_object(User, username=self.request.data['username'],
                          email=self.request.data['email'])


class ModifyEmailView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改个人邮箱
    """
    serializer_class = EmailModifySerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object(User, self.request.user.id)


class UserCourseView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户课程
    """
    serializer_class = UserCourseSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BasePagination

    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user)


class UserFavCourseView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户收藏的课程
    """
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BasePagination

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).get_fav_courses()


class UserFavOrgView(UserFavCourseView):
    """
    用户收藏的课程机构
    """
    serializer_class = CourseOrgSerializer

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).get_fav_orgs()


class UserFavTeacherView(UserFavCourseView):
    """
    用户收藏的授课教师
    """
    serializer_class = TeacherSerializer

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user.id).get_fav_teachers()


class UserMessageView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户消息列表
    """
    serializer_class = UserMessageSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BasePagination

    def get_queryset(self):
        return UserMessage.objects.filter(user=self.request.user.id)

    def list(self, request, *args, **kwargs):
        all_msg = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(all_msg)

        if page is not None:
            msg_serializer = self.get_serializer(page, many=True)
        else:
            msg_serializer = self.get_serializer(all_msg, many=True)
        # 用户进入个人消息后清空未读消息的记录
        UserMessage.objects.clean_unread_msgs()
        return Response({
            "messages": msg_serializer.data
        }, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
# @permission_classes((IsAuthenticated,))
def send_email_code(request, type, *args, **kwargs):
    """1(注册)，2(忘记密码)，3(修改邮箱)验证码发送"""
    email = request.data.get('email') or request.query_params.get('email')

    # 判断邮箱和发送类型都不为空
    if not email or not type:
        return Response(code=-1, msg="Email and type are required params.", status=status.HTTP_400_BAD_REQUEST)
    # 验证邮箱有效性
    if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$", email):
        return Response(code=-1, msg="Illegal mailbox.", status=status.HTTP_400_BAD_REQUEST)
    # 更新邮箱时需要登录用户
    if int(type) == 3:
        if not request.user.is_authenticated:
            return Response(code=-1, msg="User not logged in.", status=status.HTTP_401_UNAUTHORIZED)
        email = request.user.email
    elif int(type) == 2:
        username = request.data.get('username') or request.query_params.get('username')
        if not username:
            return Response(code=-1, msg="username is a required params.", status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(username=username, email=email):
            return Response(code=-1, msg="User is not exists, username or email error.", status=status.HTTP_401_UNAUTHORIZED)

    send_email(email, type)
    return Response(data={'type': type, 'email': email}, status=status.HTTP_200_OK)
