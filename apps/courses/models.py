# _*_ encoding:utf-8 _*_
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

from DjangoUeditor.models import UEditorField
from organization.models import CourseOrg, Teacher

User = get_user_model()


class Course(models.Model):
    DEGREE_CHOICES = (
        ("cj", "初级"),
        ("zj", "中级"),
        ("gj", "高级")
    )
    CATEGORY_CHOICES = (
        ("develop", "开发"),
        ("maintain", "运维"),
        ("test", "测试"),
        ("framework", "架构"),
    )
    # 上传课程的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    category = models.CharField(default="develop", choices=CATEGORY_CHOICES, max_length=10, verbose_name="课程类别")
    org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, null=True, blank=True, verbose_name="课程机构")
    name = models.CharField(max_length=50, verbose_name="课程名")
    desc = models.CharField(max_length=300, default='', verbose_name="课程描述")
    detail = UEditorField(verbose_name="课程详情", width=600, height=300, imagePath="courses/ueditor/",
                          filePath="courses/ueditor/", default='')
    is_banner = models.BooleanField(default=False, verbose_name="是否轮播")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, verbose_name="讲师")
    degree = models.CharField(verbose_name="难度", choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    students = models.IntegerField(db_index=True, default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(db_index=True, default=0, verbose_name='收藏人数')
    image = models.ImageField(blank=True, null=True, upload_to="courses/%Y/%m", verbose_name="封面图", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    tag = models.CharField(default="", verbose_name="课程标签", max_length=10)
    youneed_know = models.CharField(default="", max_length=300, verbose_name="课程须知")

    add_time = models.DateTimeField(db_index=True, default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'course'
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_zj_nums(self):
        # 获取课程章节数
        return self.lesson_set.all().count()

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        # 获取课程所有章节
        return self.lesson_set.all()


class BannerCourse(Course):
    class Meta:
        db_table = 'banner_course'
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True  # 不会生成新的表


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="章节名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    add_time = models.DateTimeField(db_index=True, default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'course_lesson'
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_lesson_video(self):
        # 获取章节视频
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="章节")
    name = models.CharField(max_length=100, verbose_name="视频名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    url = models.CharField(max_length=200, null=False, blank=False, verbose_name="访问地址")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'lesson_video'
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    # 上传课程资源的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="名称")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name="资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'course_resource'
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name
