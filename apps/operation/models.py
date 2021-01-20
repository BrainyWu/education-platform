# _*_ encoding:utf-8 _*_
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

from courses.models import Course
from organization.models import CourseOrg, Teacher

User = get_user_model()


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name="标题")
    image = models.ImageField(upload_to="banner/%Y/%m", verbose_name="轮播图", max_length=100)
    url = models.URLField(max_length=200, verbose_name="访问地址")
    index = models.IntegerField(default=100, verbose_name="顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'banner'
        verbose_name = "轮播图"
        verbose_name_plural = verbose_name


class UserAsk(models.Model):
    name = models.CharField(max_length=20, verbose_name="姓名")
    mobile = models.CharField(max_length=11, verbose_name="手机")
    course_name = models.CharField(max_length=50, verbose_name="课程名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'user_ask'
        verbose_name = "用户咨询"
        verbose_name_plural = verbose_name


class CourseComment(models.Model):
    """课程评论"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    comments = models.CharField(max_length=200, verbose_name="评论")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'course_comment'
        verbose_name = "课程评论"
        verbose_name_plural = verbose_name


class UserFavoriteQuerySet(models.query.QuerySet):
    """User Favorite QuerySet"""

    def get_fav_courses(self):
        fav_courses = self.filter(fav_type=1).select_related('user')
        return [Course.objects.get(id=fav_course.fav_id) for fav_course in fav_courses]

    def get_fav_orgs(self):
        fav_orgs = self.filter(fav_type=2).select_related('user')
        return [CourseOrg.objects.get(id=fav_org.fav_id) for fav_org in fav_orgs]

    def get_fav_teachers(self):
        fav_teachers = self.filter(fav_type=3).select_related('user')
        return [Teacher.objects.get(id=fav_teacher.fav_id) for fav_teacher in fav_teachers]


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    fav_id = models.IntegerField(default=0, verbose_name="数据id")
    fav_type = models.IntegerField(choices=((1, "课程"), (2, "课程机构"), (3, "讲师")), default=1, verbose_name="收藏类型")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    objects = UserFavoriteQuerySet.as_manager()

    class Meta:
        db_table = 'user_favorite'
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name


class MessageQuerySet(models.query.QuerySet):
    """User Message QuerySet"""

    def get_unread_msgs(self):
        return self.filter(has_read=False).select_related('user')

    def get_unread_msg_nums(self):
        return self.filter(has_read=False).count()

    def clean_unread_msgs(self):
        all_unread_messages = self.get_unread_msgs()
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()


class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="接收用户")
    message = models.CharField(max_length=500, verbose_name="消息内容")
    has_read = models.BooleanField(default=False, verbose_name="是否已读")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    objects = MessageQuerySet.as_manager()

    class Meta:
        db_table = 'user_message'
        verbose_name = "用户消息"
        verbose_name_plural = verbose_name


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'user_course'
        verbose_name = "用户课程"
        verbose_name_plural = verbose_name
