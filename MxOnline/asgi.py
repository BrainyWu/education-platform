# -*- coding: utf-8 -*-
__author__ = 'wuhai'
import os
import sys
import django
from channels.routing import get_default_application

app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(app_path, 'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MxOnline.setting")
django.setup()
application = get_default_application()
