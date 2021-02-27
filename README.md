# 项目说明
课程：慕课网django+xadmin打造教育平台
项目原型：https://github.com/derek-zhang123/MxOnline。
项目结构：
（1）MxOnline/conf：项目基本配置，起始路由url，ws设置。
（2）apps/extra_app：本地app应用/第三方应用开发，mvc模式设计开发。
（3）lib：公共方法集合，如：规范api统一接口response，exceptions，以及redis缓存数据库自定义拓展等。
Done:
（1）优化项目基本结构，实现django restframework开发，优化models字段关联，实现项目基本功能，添加权限控制，统一接口response，exceptions。
（2）添加全局自定义日志配置文件conf/logging.ini。
（3）优化验证码存储方式，使用redis过期校验。
（4）添加redis-session缓存方式，删除django默认session表，添加自定义过期字段expire。
（5）添加jwt模式认证，自定义jwt登陆返回格式，apps/users/utils.py。
（6）添加自定义消息通知模块notifications，app原型：django-notifications，实现基本消息通知。
（7）redis实现实例缓存，添加bloomfilter缓存校验方式。

