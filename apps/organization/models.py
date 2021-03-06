# _*_ encoding:utf-8 _*_
from datetime import datetime

from django.db import models
from DjangoUeditor.models import UEditorField


class OrgCity(models.Model):
    name = models.CharField(max_length=20, verbose_name="城市")
    desc = models.CharField(max_length=200, default="", verbose_name="描述")
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'org_city'
        verbose_name = "城市"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseOrg(models.Model):
    name = models.CharField(max_length=50, verbose_name="机构名称")
    desc = UEditorField(verbose_name="机构描述",width=900, height=300, imagePath="org/ueditor/",
                        filePath="org/ueditor/", default="")
    tag = models.CharField(default="全国知名", max_length=10, verbose_name="机构标签")
    category = models.CharField(default="pxjg", verbose_name="机构类别", max_length=20, choices=(("pxjg","培训机构"),("gr","个人"),("gx","高校")))
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    image = models.ImageField(upload_to="org/%Y/%m", blank=True, null=True, verbose_name="logo", max_length=100)
    address = models.CharField(max_length=150, default="", verbose_name="机构地址")
    city = models.ForeignKey(OrgCity, on_delete=models.CASCADE, verbose_name="所在城市")
    students = models.IntegerField(default=0, verbose_name="学习人数")
    course_nums = models.IntegerField(default=0, verbose_name="课程数")
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'course_org'
        verbose_name = "课程机构"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_teacher_nums(self):
        #获取课程机构的教师数量
        return self.teacher_set.all().count()

    def modify_fav_nums(self, incr=True):
        if incr:
            self.fav_nums += 1
        else:
            self.fav_nums -= 1
            if self.fav_nums < 0:
                self.fav_nums = 0
        self.save()
        return self.fav_nums


class Teacher(models.Model):
    org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构")
    name = models.CharField(max_length=50, verbose_name="教师名")
    work_years = models.IntegerField(default=0, verbose_name="工作年限")
    work_company = models.CharField(max_length=50, verbose_name="就职公司")
    work_position = models.CharField(max_length=50, verbose_name="公司职位")
    points = models.CharField(max_length=50, verbose_name="教学特点")
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    age = models.IntegerField(default=18, verbose_name="年龄")
    image = models.ImageField(blank=True, null=True, upload_to="teacher/%Y/%m", verbose_name="头像", max_length=100)
    created_time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'teacher'
        verbose_name = "教师"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_course_nums(self):
        return self.course_set.all().count()

    def modify_fav_nums(self, incr=True):
        if incr:
            self.fav_nums += 1
        else:
            self.fav_nums -= 1
            if self.fav_nums < 0:
                self.fav_nums = 0
        self.save()
        return self.fav_nums
