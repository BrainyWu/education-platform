# _*_ encoding:utf-8 _*_
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.views.static import serve
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from MxOnline.settings import MEDIA_ROOT, STATIC_ROOT
from users import utils
import xadmin

router = DefaultRouter()

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # jwt的认证接口
    url(r'^api-token-auth/', utils.obtain_jwt_token),
    url(r'api-token-refresh/', utils.refresh_jwt_token),
    url(r'api-token-verify/', utils.verify_jwt_token),
    # drf api接口文档
    url(r'docs/', include_docs_urls(title='API文档')),  # 线上环境，干掉

    url(r'^captcha/', include('captcha.urls')),

    # 用户相关url配置
    url(r'^u/', include(('users.urls', 'users'), namespace="user")),
    # 课程相关url
    url(r'^learn/', include(('courses.urls', 'courses'), namespace="learn")),
    # 课程机构url
    url(r'^org/', include(('organization.urls', 'organization'), namespace="organization")),
    # 操作相关url配置
    url(r'^ope/', include(('operation.urls', 'operation'), namespace="operation")),
    # 消息通知
    url(r'^notifications/', include(('notifications.urls', 'notification'), namespace="notifications")),

    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    # 富文本相关url
    url(r'^ueditor/', include(('DjangoUeditor.urls', 'ueditor'), namespace="ueditor")),
]
