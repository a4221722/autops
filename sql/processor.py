# -*- coding: UTF-8 -*- 
from .models import users
from django.conf import settings

leftMenuBtnsCommon = (
                   {'key':'allworkflow',        'name':'查看历史工单',     'url':'/allworkflow/',              'class':'glyphicon glyphicon-home'},
                   #{'key':'submitsql',          'name':'MySQL审核',       'url':'/submitsql/',               'class':'glyphicon glyphicon-asterisk'},
                   {'key':'submitsqlora',          'name':'Oracle变更申请',       'url':'/submitsqlora/',               'class':'glyphicon glyphicon-asterisk'},
                   {'key':'queryora',          'name':'Oracle查询',       'url':'/queryora/',               'class':'glyphicon glyphicon-asterisk'},
                   {'key':'oradict',          'name':'Oracle字典',       'url':'/oradict/',               'class':'glyphicon glyphicon-bookmark'},
               )
leftMenuBtnsSuper = (
                   #{'key':'masterconfig',       'name':'MySQL主库地址配置',      'url':'/admin/sql/master_config/',      'class':'glyphicon glyphicon-user'},
                   #{'key':'admin',       'name':'数据库及用户管理',      'url':'/admin/',      'class':'glyphicon glyphicon-user'},
                   {'key':'privconfig',       'name':'用户配置',      'url':'/privconfig/',      'class':'glyphicon glyphicon-th'},
    {'key': 'datasync', 'name': '数据管理', 'url': '/datasync/', 'class': 'glyphicon glyphicon-th-large'},
    {'key': 'allawr', 'name': 'awr报告', 'url': '/allawr/', 'class': 'glyphicon glyphicon-th-list'},
                   #{'key':'oraprimaryconfig',       'name':'Oracle主库地址配置',      'url':'/admin/sql/ora_primary_config/',      'class':'glyphicon glyphicon-user'},
                   #{'key':'userconfig',         'name':'用户权限配置',       'url':'/admin/sql/users/',        'class':'glyphicon glyphicon-th-large'},
                   #{'key':'workflowconfig',     'name':'所有工单管理',       'url':'/admin/sql/workflow/',        'class':'glyphicon glyphicon-list-alt'},
)
leftMenuBtnsDoc = (
                   {'key':'dbaprinciples',     'name':'SQL审核必读',       'url':'/dbaprinciples/',        'class':'glyphicon glyphicon-book'},
                   {'key':'charts',     'name':'统计图表展示',       'url':'/charts/',        'class':'glyphicon glyphicon-file'},
)


def global_info(request):
    """存放用户，会话信息等."""
    loginUser = request.session.get('login_username', None)
    if loginUser is not None:
        user = users.objects.get(username=loginUser)
        if user.is_superuser:
            leftMenuBtns = leftMenuBtnsCommon + leftMenuBtnsSuper + leftMenuBtnsDoc
        else:
            leftMenuBtns = leftMenuBtnsCommon + leftMenuBtnsDoc
    else:
        leftMenuBtns = ()

    return {
        'loginUser':loginUser,
        'leftMenuBtns':leftMenuBtns,
    }
