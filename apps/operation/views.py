# _*_ encoding:utf-8 _*_
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework_extensions.cache.decorators import cache_response

from .models import UserAsk, UserFavorite, Banner, UserCourse
from .serializers import UserAskSerializer, UserFavoriteSerializer, BannerSerializer, UserCourseSerializer
from courses.models import Course
from courses.serializers import CourseSerializer
from lib.response import Response
from lib.permissions import IsOwnerOrReadOnly, IsAdminUserOrReadOnly
from lib.utils import get_object
from organization.serializers import Teacher, CourseOrg
from notifications.views import notification_handler


class AddUserAskViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserAskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserAsk.objects.filter(user=self.request.user)


class UserCourseViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    serializer_class = UserCourseSerializer

    def get_queryset(self):
        return UserCourse.objects.all()

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnly()]


class BannerViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    serializer_class = BannerSerializer
    permission_classes = (IsAdminUserOrReadOnly,)  # 只允许管理员创建,更新和删除

    def get_queryset(self):
        return Banner.objects.all().order_by('index')

    def list(self, request, *args, **kwargs):
        all_banners = self.filter_queryset(self.get_queryset())
        banners_serializer = self.get_serializer(all_banners, many=True)
        courses = Course.objects.filter(is_banner=False)[:5]
        banner_courses = Course.objects.filter(is_banner=True)[:5]
        nb_courses_serializer = CourseSerializer(courses, many=True)
        b_courese_serializer = CourseSerializer(banner_courses, many=True)
        return Response({
            'all_banners': banners_serializer.data,
            'not_banner_courses': nb_courses_serializer.data,
            'banner_courses': b_courese_serializer.data,
        }, status=status.HTTP_200_OK)


class AddFavViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """添加, 取消收藏(1, "课程"), (2, "课程机构"), (3, "讲师")"""
    serializer_class = UserFavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related('user')

    def obj_map(self, fav_type=None, fav_id=None):
        if int(fav_type) == 1:
            obj = get_object(Course, object_id=int(fav_id))
        elif int(fav_type) == 2:
            obj = get_object(CourseOrg, object_id=int(fav_id))
        elif int(fav_type) == 3:
            obj = get_object(Teacher, object_id=int(fav_id))
        else:
            raise ValueError("Fav type incorrect.")
        return obj

    def create(self, request, *args, **kwargs):
        fav_id = request.data.get('fav_id', None)
        fav_type = request.data.get('fav_type', None)
        if fav_id is None or fav_type is None:
            return Response(code=-1, msg='Fav_id and Fav type are required.', status=status.HTTP_400_BAD_REQUEST)

        obj = self.obj_map(fav_type, fav_id)
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 记录已经存在， 则表示用户取消收藏, fav_nums减一
            exist_records.delete()
            obj.modify_fav_nums(incr=False)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 记录不存在， 则表示用户收藏, fav_nums加一
            user_fav = UserFavorite()
            user_fav.create(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
            # 点赞课程才通知
            if int(fav_type) == 1:
                notification_handler(self.request.user, obj.user, 'L', obj)
            obj.modify_fav_nums(incr=True)
            return Response(status=status.HTTP_201_CREATED)
