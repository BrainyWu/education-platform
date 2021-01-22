# _*_ encoding:utf-8 _*_
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_extensions.cache.decorators import cache_response

from .models import UserAsk, UserFavorite, Banner, UserCourse
from .serializers import UserAskSerializer, UserFavoriteSerializer, BannerSerializer, UserCourseSerializer
from courses.models import Course
from courses.serializers import CourseSerializer
from lib.response import Response
from lib.permissions import IsOwnerOrReadOnly, IsAdminUserOrReadOnly
from organization.serializers import Teacher, CourseOrg


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
    permission_classes = (IsAdminUserOrReadOnly, )  # 只允许管理员创建,更新和删除

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
    """添加收藏(1, "课程"), (2, "课程机构"), (3, "讲师")"""
    serializer_class = UserFavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related('user')

    def create(self, request, *args, **kwargs):
        fav_id = request.data.get('fav_id', 0)
        fav_type = request.data.get('fav_type', 0)

        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在， 则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                else:
                    return Response(
                        code=-1,
                        msg='Fav type is invalid.',
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(
                    code=-1,
                    msg='Add favorite fail.',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
