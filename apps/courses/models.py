# _*_ encoding:utf-8 _*_
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.core.serializers import serialize

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
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'course'
        verbose_name = "课程"
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )

    def __str__(self):
        return self.name

    def get_zj_nums(self):
        # 获取课程章节数
        return self.lesson_set.all().count()

    def get_learn_users(self):
        return [obj.user.username for obj in self.usercourse_set.all()][:10]

    def get_lessons(self):
        # 获取课程所有章节
        return [{'id': obj.id, 'name': obj.name, 'videos': obj.get_videos()}
                for obj in self.lesson_set.all()]

    def modify_fav_nums(self, incr=True):
        if incr:
            self.fav_nums += 1
        else:
            self.fav_nums -= 1
            if self.fav_nums < 0:
                self.fav_nums = 0
        self.save()
        return self.fav_nums


class BannerCourse(Course):
    class Meta:
        db_table = 'banner_course'
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True  # 不会生成新的表
        ordering = ('-created_time', )


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="章节名")
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'course_lesson'
        verbose_name = "章节"
        verbose_name_plural = verbose_name
        ordering = ('course', '-created_time')

    def __str__(self):
        return self.name

    def get_videos(self):
        # 章节视频
        return serialize('json', self.video_set.all())
        # return [{'name': obj.name, 'learn_times': obj.learn_times, 'url': obj.url, 'created_time': obj.created_time}
        #         for obj in self.video_set.all()]


class VideoQuerySet(models.query.QuerySet):

    def get_course_videos(self, cid=None):
        return self.filter(course=cid)

    def get_lesson_videos(self, lid=None):
        return self.filter(lesson=lid)


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="章节")
    name = models.CharField(max_length=100, verbose_name="视频名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    url = models.CharField(max_length=200, null=False, blank=False, verbose_name="访问地址")
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = VideoQuerySet.as_manager()

    class Meta:
        db_table = 'lesson_video'
        verbose_name = "视频"
        verbose_name_plural = verbose_name
        ordering = ('lesson', '-created_time')

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    # 上传课程资源的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="名称")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name="资源文件", max_length=100)
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'course_resource'
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name
        ordering = ('course', '-created_time')
