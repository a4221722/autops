#e -*- coding: UTF-8 -*- 
import re
from django.http import HttpResponseRedirect,HttpResponseNotFound
import json

class CheckLoginMiddleware(object):
    def process_request(self, request):
        """
        该函数在每个函数之前检查是否登录，若未登录，则重定向到/login/
        """
        """
        检查是否公网访问
        """
        remoteIp = request.META.get('HTTP_X_FORWARDED_FOR',request.META['REMOTE_ADDR'])
        if not remoteIp.startswith('192.168') and not remoteIp.startswith('10.') and request.path not in ('/login/','/logout/', '/authenticate/') and not re.match(r'^/detail/(?P<workflowId>[0-9]+)/$',request.path) and not re.match(r'^/execute/$',request.path) and not re.match(r'^/cancel/$',request.path):
            return HttpResponseNotFound()
        if request.session.get('login_username', False) in (False, '匿名用户'):
            #以下是不用跳转到login页面的url白名单
            if request.path not in ('/login/', '/authenticate/') and re.match(r"/admin/\w*", request.path) is None:
                return HttpResponseRedirect('/login/?originPath='+request.path)
