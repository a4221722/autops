# -*- coding: UTF-8 -*- 

from django.conf.urls import url,include
from . import views

urlpatterns = [
    url(r'^allawr/$', views.allAwr, name='allawr'),
    url(r'^awrdisplay/$', views.awrDisplay, name='awrdisplay'),
    url(r'^generatesnap/$', views.generateSnap, name='generatesnap'),
    url(r'^statcollect/$', views.statCollect, name='statcollect'),
]
