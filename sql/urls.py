# -*- coding: UTF-8 -*- 

from django.conf.urls import url,include
from . import views, views_ajax

urlpatterns = [
    url(r'^$', views.allworkflow, name='allworkflow'),
    url(r'^index/$', views.allworkflow, name='allworkflow'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^submitsqlora/$',views.submitSqlOra,name='submitSqlOra'),
    #url(r'editsql/workflowid=(?P<workflowId>[0-9]+)/$', views.submitSqlOra, name='editsql'),
    url(r'editsql/$', views.submitSqlOra, name='editsql'),
    url(r'^allworkflow/$', views.allworkflow, name='allworkflow'),
    
    url(r'^workflowsubmit/$', views.workflowSubmit, name='workflowsubmit'),
    url(r'^detail/(?P<workflowId>[0-9]+)/$', views.detail, name='detail'),
    url(r'^execute/$', views.execute, name='execute'),
    url(r'^cancel/$', views.cancel, name='cancel'),
    url(r'^datasync/$', views.datasync, name='datasync'),
    url(r'^dbaprinciples/$', views.dbaprinciples, name='dbaprinciples'),
    url(r'^charts/$', views.charts, name='charts'),
    url(r'^queryora/$', views.queryora, name='queryora'),
    url(r'^oradict/$', views.oradict, name='oradict'),
    url(r'^privconfig/$', views.privConfig, name='privconfig'),
    url(r'^myprivs/$', views.myPrivs, name='myprivs'),

    url(r'^myprofile/$', views.myProfile, name='myprofile'),

    url(r'^authenticate/$', views_ajax.authenticateEntry, name='authenticate'),
    url(r'^syncldapuser/$', views_ajax.syncldapuser, name='syncldapuser'),
    url(r'^syncoradict/$', views_ajax.syncoradict, name='syncoradict'),
    url(r'^orasimplecheck/$', views_ajax.orasimplecheck, name='orasimplecheck'),
    url(r'^getMonthCharts/$', views_ajax.getMonthCharts, name='getMonthCharts'),
    url(r'^getPersonCharts/$', views_ajax.getPersonCharts, name='getPersonCharts'),
    #url(r'^getOscPercent/$', views_ajax.getOscPercent, name='getOscPercent'),
    url(r'^getWorkflowStatus/$', views_ajax.getWorkflowStatus, name='getWorkflowStatus'),
    url(r'^stopOscProgress/$', views_ajax.stopOscProgress, name='stopOscProgress'),
    url(r'^manexec/$', views_ajax.manExec, name='manualexecute'),
    url(r'^manfinish/$', views_ajax.manFinish, name='manualFinish'),
    url(r'^privmod/(?P<operation>\w+)/$', views_ajax.privMod, name='privmod'),
    url(r'^privcommit/(?P<operation>\w+)/$', views_ajax.privCommit, name='privcommit'),
    url(r'^getresult/$', views_ajax.getResult, name='getresult'),
    url(r'^engineeraffirm/$', views.engineerAffirm, name='engineeraffirm'),
    url(r'^assigntome/$', views.assignToMe, name='assigntome'),
]
