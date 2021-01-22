# _*_ encoding:utf-8 _*_
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .models import CourseOrg, OrgCity, Teacher
from .serializers import CourseOrgSerializer, CitySerializer, TeacherSerializer
from courses.models import Course
from courses.serializers import CourseSerializer
from lib.utils import BasePagination, get_object
from lib.response import Response
from operation.models import UserFavorite


class OrgViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """机构"""
    serializer_class = CourseOrgSerializer
    pagination_class = BasePagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ("name", "category", 'city')
    search_fields = ("name", "desc")
    ordering_fields = ("students", "click_nums", "_time", "course_nums")
    lookup_field = 'id'

    # def get_permissions(self):
    #     if self.action == "list" or self.action == "retrieve":
    #         return []
    #     else:
    #         return [IsAuthenticated()]

    def get_queryset(self):
        return CourseOrg.objects.all().select_related('city')

    def retrieve(self, request, *args, **kwargs):
        org = self.get_object()
        org.click_nums += 1
        org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=org.id, fav_type=2):
                has_fav = True
        serializer = self.get_serializer(org)
        return Response({
            'course_org': serializer,
            'has_fav': has_fav
        })


class CityViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """机构驻地"""
    serializer_class = CitySerializer
    pagination_class = BasePagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "desc")
    ordering_fields = ("created_time",)

    def get_queryset(self):
        return OrgCity.objects.all()


class TeacherViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    机构教师
    """
    serializer_class = TeacherSerializer
    pagination_class = BasePagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ("name", "work_company", 'work_position')
    search_fields = ("name",)
    ordering_fields = ("click_nums",)
    lookup_field = 'id'

    def get_queryset(self):
        return Teacher.objects.all().select_related('org')

    def list(self, request, *args, **kwargs):
        org_id = request.query_params.get('org_id', None)

        if org_id:
            course_org = get_object(CourseOrg, org_id)
            has_fav = False
            if request.user.is_authenticated:
                if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                    has_fav = True
            teachers = course_org.teacher_set.all()
            teachers_serializer = self.get_serializer(teachers, many=True)
            return Response({
                'teachers': teachers_serializer.data,
                'has_fav': has_fav
            })
        else:
            teachers_serializer = self.get_serializer(self.get_queryset(), many=True)
            return Response({
                'teachers': teachers_serializer.data,
            })

    def retrieve(self, request, *args, **kwargs):
        teacher = self.get_object()
        teacher_serializer = self.get_serializer(teacher)
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)
        courses_serializer = CourseSerializer(all_courses, many=True)

        has_teacher_faved = False
        has_org_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                has_teacher_faved = True
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True
        return Response({
            "teacher": teacher_serializer.data,
            "rel_courses": courses_serializer.data,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved
        })
