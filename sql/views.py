# -*- coding: UTF-8 -*- 

import re
import json
import multiprocessing
import math
from collections import OrderedDict
import pdb

from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger

from .daoora import DaoOra
from .const import Const
from .sendmail import MailSender
from .aes_decryptor import Prpcrypt
from .models import *
from .getnow import getNow
from .tasks import oraAutoReview,mailDba,wechatDba,dingDba

daoora = DaoOra()
prpCryptor = Prpcrypt()
cryColList = ['cert_no','qq','cell','card_no']

configMap = {
    'oracle':ora_primary_config,
    'mysql':'my_primary_config'}
daoMap = {
    'oracle':daoora,
    'mysql':'my_master_config'}

def login(request):
    if request.GET.get('originPath') is not None and re.match(r'/detail/(?P<workflowId>[0-9]+)/$',request.GET.get('originPath')):
        origin_path = request.GET.get('originPath')
    else:
        origin_path = '/allworkflow/'
    context={'origin_path':origin_path}
    return render(request, 'login.html',context)

def logout(request):
    if request.session.get('login_username', False):
        del request.session['login_username']
    return render(request, 'login.html')

def _mapRmDisplay(reviewMan):
    try:
        userList = json.loads(reviewMan)
    except Exception:
        userList = reviewMan
    displayList = [users.objects.get(username=un).display for un in userList]
    return displayList

def _mapEnDisplay(userName):
    try:
        display=users.objects.get(username=userName).display
    except Exception:
        display=''
    return display

#首页，也是查看所有SQL工单页面，具备翻页功能
def allworkflow(request):
    #一个页面展示
    PAGE_LIMIT = 12

    pageNo = 0
    navStatus = ''
    listAllWorkflow = []


    #if 'navStatus' in request.GET:
    #    navStatus = request.GET['navStatus']
    #else:
    #    navStatus = 'all'
    hasAffirmed = request.GET.get('hasAffirmed')
    searchStatus = request.GET.get('search_status')
    waitForPrc = request.GET.get('wait_process')

    loginUser = request.session.get('login_username', False)
    #修改全部工单、审核不通过、已执行完毕界面工程师只能看到自己发起的工单，审核人可以看到全部
    allFlow = []
    listWorkflow = []
    #查询全部流程
    loginUserOb = users.objects.get(username=loginUser)
        
    #查询workflow model，根据pageNo和navStatus获取对应的内容
    role = loginUserOb.role
    if role == '审核人' or loginUser == 'admin':
        allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').order_by('-create_time')
    elif role == '工程师':
        allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(engineer=loginUser).order_by('-create_time')
    #if navStatus == 'all' and (role == '审核人' or loginUser == 'admin'):
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').order_by('-create_time')
    #elif navStatus == 'all' and role == '工程师':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(engineer=loginUser).order_by('-create_time')
    #elif navStatus == 'waitingforme':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(Q(status__in=(Const.workflowStatus['manreviewing'],Const.workflowStatus['manexec'],Const.workflowStatus['autoreviewwrong']),review_man__icontains=loginUser ) | Q(status__in=(Const.workflowStatus['manreviewing'],Const.workflowStatus['manexec']), review_man__contains='"' + loginUser + '"')).order_by('-create_time')
    #elif (role == '审核人' or loginUser == 'admin') and navStatus == 'unaffirm':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(status__in=(Const.workflowStatus['finish'],Const.workflowStatus['manfinish'],),affirm = '未确认').order_by('-create_time')
    #elif role == '工程师'  and navStatus == 'unaffirm':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(engineer=loginUser,status__in=(Const.workflowStatus['finish'],Const.workflowStatus['manfinish'],),affirm = '未确认').order_by('-create_time')
    #elif (role == '审核人' or loginUser == 'admin') and navStatus == 'affirm':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(status__in=(Const.workflowStatus['finish'],Const.workflowStatus['manfinish'],),affirm = '已确认').order_by('-create_time')
    #elif role == '工程师'  and navStatus == 'affirm':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(engineer=loginUser,status__in=(Const.workflowStatus['finish'],Const.workflowStatus['manfinish'],),affirm = '已确认').order_by('-create_time')
    #    #allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','create_time','cluster_name').filter(status__in=(Const.workflowStatus['finish'],Const.workflowStatus['exception'],Const.workflowStatus['manfinish'],Const.workflowStatus['manexcept'])).order_by('-create_time')
    #elif role == '工程师':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(status__in=(Const.workflowStatus['finish'],Const.workflowStatus['exception'],Const.workflowStatus['manfinish'],Const.workflowStatus['manexcept']),engineer=loginUser).order_by('-create_time')
    #elif role == '审核人' or loginUser == 'admin':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(status=Const.workflowStatus[navStatus]).order_by('-create_time')
    #elif role == '工程师':
    #    allFlow = workflow.objects.values('id','data_change_type','workflow_name','engineer','status','affirm','create_time','cluster_name').filter(status=Const.workflowStatus[navStatus],engineer=loginUser).order_by('-create_time')
    #else:
    #    context = {'errMsg': '传入参数有误！'}
    #    return render(request, 'error.html', context)
    if hasAffirmed:
        allFlow = allFlow.filter(affirm = hasAffirmed)
    if searchStatus:
        allFlow = allFlow.filter(status = searchStatus)
    if waitForPrc and waitForPrc == '待我处理':
        allFlow = allFlow.filter(review_man__contains='"' + loginUser + '"',status__in = (Const.workflowStatus['manreviewing'],Const.workflowStatus['autoreviewwrong'],Const.workflowStatus['manexec']))
    pages = math.ceil(len(allFlow)/PAGE_LIMIT)
    pageList = [i+1 for i in range(0,pages)]
    #参数检查
    if 'pageNo' in request.GET:
        pageNo = min(int(request.GET['pageNo']),pages)
    else:
        pageNo = 1
    if pageNo < 1:
        pageNo = 1
    offset = (pageNo-1) * PAGE_LIMIT
    limit = offset + PAGE_LIMIT
    listWorkflow = allFlow[offset:limit]
    pageDisplay = [pageNo+i for i in range(-5,5) if pageNo+i>0 and pageNo+i<=pages]
    for flow in listWorkflow:
        flow['engineer_display']=_mapEnDisplay(flow['engineer'])
    flowStatus = [v for k,v in Const.workflowStatus.items()]

    #context = {'currentMenu':'allworkflow', 'listWorkflow':listWorkflow,'pages':pages, 'pageNo':pageNo, 'navStatus':navStatus, 'PAGE_LIMIT':PAGE_LIMIT, 'role':role, 'flowStatus':flowStatus}
    return render(request, 'allWorkflow.html', locals())


#提交oracle sql界面
def submitSqlOra(request,workflowId=None):
    workflowId = request.GET.get('workflowid')
    if workflowId:
        workflowDetail = get_object_or_404(workflow, pk=workflowId)
        sql_content = workflowDetail.sql_content
        workflow_name = workflowDetail.workflow_name
        cluster_name = workflowDetail.cluster_name.split(',')
        message = workflowDetail.message
        reason = workflowDetail.reason
        data_change_type = workflowDetail.data_change_type

    primaries = ora_primary_config.objects.all().order_by('cluster_name')
    if len(primaries) == 0:
        context = {'errMsg': '目标数为0, 请查看后端是否没有配置数据库信息'}
        return render(request, 'error.html', context)

    #获取所有数据库名称
    listAllClusterName = [primary.cluster_name for primary in primaries]
    
    dictAllClusterSchema = OrderedDict()
    ##获取主库地址:
    for clusterName in listAllClusterName:
    #    listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
    #    if len(listPrimaries) !=1:
    #        context = {'errMsg': '存在两个名称一样的数据库，请修改数据库配置'}
    #        return render(request, 'error.html', context)
    #    #取出连接信息
    #    primaryHost = listPrimaries[0].primary_host
    #    primaryPort = listPrimaries[0].primary_port
    #    primarySrv = listPrimaries[0].primary_srv
    #    primaryUser = listPrimaries[0].primary_user
    #    primaryPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)

    #    listSchema = daoora.getAllSchemaByCluster(clusterName)
        dictAllClusterSchema[clusterName] = ''

    #获取所有审核人，当前登录用户不可以审核
    loginUser = request.session.get('login_username', False)
    reviewMen = users.objects.filter(role='审核人').exclude(username=loginUser)
    if len(reviewMen) == 0:
       context = {'errMsg': '审核人为0，请配置审核人'}
       return render(request, 'error.html', context)
    listAllReviewMen = [user.display for user in reviewMen]
    if workflowId:
        context = {'currentMenu':'submitsqlora', 'dictAllClusterSchema':dictAllClusterSchema, 'reviewMen':listAllReviewMen,'workflowid':workflowId,'sql_content':sql_content,'workflow_name':workflow_name,'message':message,'reason':reason,'data_change_type':data_change_type}
    else:
        context = {'currentMenu':'submitsqlora', 'dictAllClusterSchema':dictAllClusterSchema, 'reviewMen':listAllReviewMen}
    return render(request, 'submitSqlOra.html', context)


#将中文名映射为英文名
def _mapReviewMan(review_man):
    usersList = users.objects.filter(display=review_man)
    listUsername = [user.username for user in usersList]
    return listUsername[0]

#判断工单类型，做相应处理
def workflowSubmit(request):
    dataChangeType = request.POST.get('data_change_type')
    workflowid = request.POST.get('workflowid')
    sqlContent = request.POST['sql_content']
    workflowName = request.POST['workflow_name']
    clusterNameStr = request.POST.get('cluster_name')
    isBackup = request.POST['is_backup']
    reviewMan = request.POST.get('review_man').split(',')
    listAllReviewMen = [_mapReviewMan(man) for man in reviewMan]
    message = request.POST['message']
    reason = request.POST['reason']
    data_change_type = request.POST['data_change_type']
    #subReviewMen = _mapReviewMan(request.POST.get('sub_review_man', ''))


    #服务器端参数验证
    if data_change_type in ('数据修订','数据初始化'):
        if sqlContent is None:
            context = {'errMsg': 'SQL内容不能为空'}
            return render(request, 'error.html', context)
    else:
        if message is None:
            context = {'errMsg': '备注不能为空'}
            return render(request, 'error.html', context)
    if reason is  None or workflowName is None or clusterNameStr is None or isBackup is None or reviewMan is None:
        context = {'errMsg': '页面提交参数可能为空'}
        return render(request, 'error.html', context)


    primaries = ora_primary_config.objects.all().order_by('cluster_name')
    if len(primaries) == 0:
        context = {'errMsg': '目标数为0, 请查看后端是否没有配置数据库信息'}
        return render(request, 'error.html', context)

    #获取所有数据库名称
    listAllClusterName = [primary.cluster_name for primary in primaries]
    
    dictAllClusterSchema = OrderedDict()
    #获取主库地址:
    for clusterName in listAllClusterName:
        listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
        if len(listPrimaries) !=1:
            context = {'errMsg': '存在两个名称一样的数据库，请修改数据库配置'}
            return render(request, 'error.html', context)
        #取出连接信息
        primaryHost = listPrimaries[0].primary_host
        primaryPort = listPrimaries[0].primary_port
        primarySrv = listPrimaries[0].primary_srv
        primaryUser = listPrimaries[0].primary_user
        primaryPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)
    
    #判断工单类型，转入相应的状态
    if data_change_type in ('数据修订','数据初始化') and sqlContent:
        sqlContent = sqlContent.rstrip()
        if sqlContent[-1] != ";":
            context = {'errMsg': "SQL语句结尾没有以;结尾，请后退重新修改并提交！"}
            return render(request, 'error.html', context)

        workflowStatus = Const.workflowStatus['autoreviewing']
    else:
        workflowStatus = Const.workflowStatus['manexec']


    #存进数据库里
    engineer = request.session.get('login_username', False)
    if not workflowid:
        Workflow = workflow()
        Workflow.create_time = getNow()
    else:
        Workflow = workflow.objects.get(id=int(workflowid))
    Workflow.workflow_name = workflowName
    Workflow.engineer = engineer
    Workflow.review_man = json.dumps(listAllReviewMen, ensure_ascii=False)
    Workflow.status = workflowStatus
    Workflow.is_backup = isBackup
    Workflow.cluster_name = clusterNameStr
    Workflow.sql_content = sqlContent
    Workflow.execute_result = ''
    Workflow.message = message
    Workflow.reason = reason
    Workflow.data_change_type = data_change_type
    Workflow.save()
    workflowId = Workflow.id
    if data_change_type in ('数据修订','数据初始化') and sqlContent:
        oraAutoReview.delay(workflowId)

    url = _getDetailUrl(request) + str(workflowId) +'/'
    strTitle = "新的SQL上线工单提醒 # " + str(workflowId)
    objEngineer = users.objects.get(username=engineer)
    for reviewMan in listAllReviewMen:
        if reviewMan == "":
            continue
        strContent = "发起人：" + engineer + "\n审核人：" + str(listAllReviewMen)  + "\n工单地址：" + url + "\n工单名称： " + workflowName+"\n原因:"+ reason+"\n备注说明: "+ message + "\n具体SQL：" + sqlContent
        objReviewMan = users.objects.get(username=reviewMan)
        mailDba.delay(strTitle, strContent, [objReviewMan.email])
        wechatDba.delay(strTitle,strContent,objReviewMan.wechat_account)
        dingDba.delay(strContent,objReviewMan.mobile)

    return HttpResponseRedirect('/detail/' + str(workflowId) + '/') 


def _mapResultSt(x):
    if x['stagestatus'] == '连接服务器异常':
        return 1
    elif x['stagestatus'] == 'sql执行异常':
        return 2
    elif x['stagestatus'] == '解析失败':
        return 3
    else:
        return 4


#展示SQL工单详细内容，以及可以人工审核，审核通过即可执行
def detail(request, workflowId):
    PAGE_LIMIT = 12
    pageNo = 0

    if 'pageNo' in request.GET:
        pageNo = min(int(request.GET['pageNo']),pages-1)
    else:
        pageNo = 0
    if pageNo < 0:
        pageNo = 0
    offset = pageNo * PAGE_LIMIT
    limit = offset + PAGE_LIMIT

    loginUser = request.session.get('login_username', False)
    loginUserObj = users.objects.get(username = loginUser)
    workflowDetail = get_object_or_404(workflow, pk=workflowId)
    if workflowDetail.status in (Const.workflowStatus['finish'], Const.workflowStatus['exception'],Const.workflowStatus['manfinish'],Const.workflowStatus['manexcept']):
        try:
            listResult = json.loads(workflowDetail.execute_result)
            listResult.sort(key=_mapResultSt)
        except Exception as err:
            listResult = []
    else:
        if workflowDetail.review_content:
            listResult = json.loads(workflowDetail.review_content)
        else:
            listResult=[]
    pages = math.ceil(len(listResult)/PAGE_LIMIT)
    pageRange = range(pageNo,pageNo+min(4,pages-pageNo)+1)
    listContent = listResult[offset:limit]
    try:
        listAllReviewMen = json.loads(workflowDetail.review_man)
    except ValueError:
        listAllReviewMen = (workflowDetail.review_man, )
    strMessage = workflowDetail.message
    workflowStatus = Const.workflowStatus
    engineer_display = _mapEnDisplay(workflowDetail.engineer)
    reviewman_display = _mapRmDisplay(workflowDetail.review_man)
    operator_display = _mapEnDisplay(workflowDetail.operator)

    context = {'currentMenu':'allworkflow', 'workflowDetail':workflowDetail, 'listContent':listContent,'pages':pages,'pageNo':pageNo,'PAGE_LIMIT':PAGE_LIMIT,'listAllReviewMen':listAllReviewMen,'pageRange':pageRange,'strMessage':strMessage,'loginUserObj':loginUserObj,'workflowStatus':workflowStatus,'engineer_display':engineer_display,'reviewman_display':reviewman_display,'operator_display':operator_display}
    return render(request, 'detail.html', context)
#人工审核也通过，执行SQL
def execute(request):
    workflowId = request.POST['workflowid']
    if workflowId == '' or workflowId is None:
        context = {'errMsg': 'workflowId参数为空.'}
        return render(request, 'error.html', context)
    
    workflowId = int(workflowId)
    with transaction.atomic():
        try:
            workflowDetail = workflow.objects.select_for_update().get(id=workflowId,status__in=(Const.workflowStatus['manreviewing'],Const.workflowStatus['autoreviewwrong'],))
        except Exception:
            context = {'errMsg': '已经在执行'}
            return render(request, 'error.html', context)

    #clusterName = workflowDetail.cluster_name
    try:
        listAllReviewMen = json.loads(workflowDetail.review_man)
    except ValueError:
        listAllReviewMen = (workflowDetail.review_man, )

    #服务器端二次验证，正在执行人工审核动作的当前登录用户必须为审核人. 避免攻击或被接口测试工具强行绕过
    loginUser = request.session.get('login_username', False)
    if loginUser is None or loginUser not in listAllReviewMen:
        context = {'errMsg': '当前登录用户不是审核人，请重新登录.'}
        return render(request, 'error.html', context)


    #将流程状态修改为执行中，并更新reviewok_time字段
    workflowDetail.status = Const.workflowStatus['executing']
    workflowDetail.reviewok_time = getNow()
    workflowDetail.save()


    (finalStatus, finalList) = daoora.executeFinal(workflowDetail)

    #封装成JSON格式存进数据库字段里
    strJsonResult = json.dumps(finalList)
    workflowDetail.execute_result = strJsonResult
    workflowDetail.finish_time = getNow()
    workflowDetail.status = finalStatus
    workflowDetail.operator = loginUser
    workflowDetail.save()

    #如果执行完毕了，则根据settings.py里的配置决定是否给提交者和DBA一封邮件提醒.DBA需要知晓审核并执行过的单子
    url = _getDetailUrl(request) + str(workflowId) + '/'

    #给主、副审核人，申请人，DBA各发一封邮件
    engineer = workflowDetail.engineer
    reviewMen = workflowDetail.review_man
    workflowStatus = workflowDetail.status
    workflowName = workflowDetail.workflow_name
    objEngineer = users.objects.get(username=engineer)
    strTitle = "SQL上线工单执行完毕 # " + str(workflowId)
    strContent = "发起人：" + engineer + "\n审核人：" + reviewMen + "\n工单地址：" + url + "\n工单名称： " + workflowName +"\n执行结果：" + workflowStatus
    mailDba.delay(strTitle, strContent, [objEngineer.email])
    wechatDba.delay(strTitle, strContent,objEngineer.wechat_account)
    dingDba.delay(strContent,objEngineer.mobile)

    return HttpResponseRedirect('/detail/' + str(workflowId) + '/') 

#终止流程
def cancel(request):
    workflowId = request.POST['workflowid']
    if workflowId == '' or workflowId is None:
        context = {'errMsg': 'workflowId参数为空.'}
        return render(request, 'error.html', context)

    workflowId = int(workflowId)
    workflowDetail = workflow.objects.get(id=workflowId)
    reviewMan = workflowDetail.review_man
    try:
        listAllReviewMen = json.loads(reviewMan)
    except ValueError:
        listAllReviewMen = (reviewMan, )

    #服务器端二次验证，如果正在执行终止动作的当前登录用户，不是发起人也不是审核人，则异常.
    loginUser = request.session.get('login_username', False)
    if loginUser is None or (loginUser not in listAllReviewMen and loginUser != workflowDetail.engineer):
        context = {'errMsg': '当前登录用户不是审核人也不是发起人，请重新登录.'}
        return render(request, 'error.html', context)

    #服务器端二次验证，如果当前单子状态是结束状态，则不能发起终止
    if workflowDetail.status in (Const.workflowStatus['abort'], Const.workflowStatus['finish'], Const.workflowStatus['manfinish']):
        return HttpResponseRedirect('/detail/' + str(workflowId) + '/')

    workflowDetail.status = Const.workflowStatus['abort']
    workflowDetail.save()
	
    #如果人工终止了，则根据settings.py里的配置决定是否给提交者和审核人发邮件提醒。如果是发起人终止流程，则给主、副审核人各发一封；如果是审核人终止流程，则给发起人发一封邮件，并附带说明此单子被拒绝掉了，需要重新修改.
    url = _getDetailUrl(request) + str(workflowId) + '/'

    engineer = workflowDetail.engineer
    workflowStatus = workflowDetail.status
    workflowName = workflowDetail.workflow_name
    if loginUser == engineer:
        strTitle = "发起人主动终止SQL上线工单流程 # " + str(workflowId)
        strContent = "发起人：" + engineer + "\n审核人：" + reviewMan + "\n工单地址：" + url + "\n工单名称： " + workflowName +"\n执行结果：" + workflowStatus +"\n提醒：发起人主动终止流程"
        for reviewMan in listAllReviewMen:
            if reviewMan == "":
                continue
            objReviewMan = users.objects.get(username=reviewMan)
            mailDba.delay(strTitle, strContent, [objReviewMan.email])
            wechatDba.delay(strTitle, strContent, objReviewMan.wechat_account)
            dingDba.delay(strContent,objReviewMan.mobile)
    else:
        objEngineer = users.objects.get(username=engineer)
        strTitle = "SQL上线工单被拒绝执行 # " + str(workflowId)
        strContent = "发起人：" + engineer + "\n审核人：" + reviewMan + "\n工单地址：" + url + "\n工单名称： " + workflowName +"\n执行结果：" + workflowStatus +"\n提醒：此工单被拒绝执行，请登陆重新提交或修改工单"
        mailDba.delay(strTitle, strContent, [objEngineer.email])
        wechatDba.delay(strTitle, strContent, objEngineer.wechat_account)
        dingDba.delay(strContent,objEngineer.mobile)

    return HttpResponseRedirect('/detail/' + str(workflowId) + '/')

#工程师确认
def engineerAffirm(request):
    loginUser = request.session.get('login_user')
    workflowId = request.POST['workflowid']
    with transaction.atomic():
        try:
            workflowDetail = workflow.objects.select_for_update().get(id=workflowId,status__in=(Const.workflowStatus['finish'],Const.workflowStatus['manfinish'],))
        except Exception:
            context = {'errMsg': '在操作中'}
            return render(request, 'error.html', context)
        workflowDetail.affirm = '已确认'
        workflowDetail.affirm_time = getNow()
        workflowDetail.save()
    return HttpResponseRedirect('/detail/' + str(workflowId) + '/')

#检查登录用户是否为admin
def check_admin(func):
    def _decrator(request):
        loginUser = request.session.get('login_username', False)
        if loginUser != 'admin':
            context = {'errMsg': '无权限访问该页面'}
            return render(request, 'error.html', context)
        else:
            return func(request)
    return _decrator

#数据同步
@check_admin
def datasync(request):
    optCtls = operation_ctl.objects.all().order_by('data_type').order_by('opt_type')
    optDict = {}
    for optCtl in optCtls:
        optDict[optCtl.data_type+'_'+optCtl.opt_type]=[optCtl.modify_time.strftime("%Y-%m-%d %H:%M:%S"),optCtl.status]
    #optDict = json.dumps(optDict)
    listOptInfo = operation_record.objects.all().order_by('-modify_time')[:10]
    for row in listOptInfo:
        #row.message = row.message[max(row.message.rfind('$$',0,-3)+2,len(row.message)-50):row.message.rfind('$$')]
        for i in ['create_time','modify_time','finish_time']:
            if getattr(row,i) is not None:
                setattr(row,i,getattr(row,i).strftime('%Y-%m-%d %H:%M:%S'))
    context = {'currentMenu':'datasync','optDict':optDict,'listOptInfo':listOptInfo}
    return render(request, 'datasync.html', context)

#查询功能
@csrf_exempt
def queryora(request):
    primaries = ora_primary_config.objects.all().order_by('cluster_name')
    if len(primaries) == 0:
        context = {'errMsg': '目标数为0, 请查看后端是否没有配置数据库信息'}
        return render(request, 'error.html', context)
    #获取所有数据库名称
    listAllClusterName = [primary.cluster_name for primary in primaries]
    
    dictAllClusterSchema = OrderedDict()
    for clusterName in listAllClusterName:
        dictAllClusterSchema[clusterName] = ''

    #query = request.POST.get('query')
    #if query and query == '1':
    logon_user = request.session.get('login_username', False)
    clusterName = request.POST.get('cluster_name')
    sql_content = request.POST.get('sql_content')
    sql_query = request.POST.get('sql_query')
    try:
        page = int(request.POST.get('page','1'))
    except Exception:
        page = 1
    headerList = []
    queryResultP = []
    after_range_num = 5
    before_range_num = 4
    if page < 1:
        page = 1
    if sql_query:
        sqlContent = sql_query.strip().rstrip(';')
        if len(sqlContent) == 0:
            context = {'errMsg':'sql内容不能为空'}
            return render(request,'error.html',context)
        finalStatus,msg,headerList,queryResult = daoora.query(logon_user,clusterName,sqlContent)
        paginator = Paginator(queryResult, 10)
        try:
            queryResultP = paginator.page(page)
        except (EmptyPage,InvalidPage,PageNotAnInteger):
            queryResultP = paginator.page(1)
        if page >= after_range_num:
            page_range = paginator.page_range[page-after_range_num:page+before_range_num]
        else:
            page_range = paginator.page_range[0:int(page)+before_range_num]
        if finalStatus != '执行结束':
            context = {'errMsg':msg}
            return render(request, 'error.html', context)
        header_list = headerList
        crtList = []
        for cnt in range(0,len(headerList)):
            if headerList[cnt].lower() in cryColList:
                crtList.append(cnt)
        query_result_p = []
        for row in queryResultP:
            strRow = []
            for i in range(0,len(row)):
                if i in crtList:
                    strRow.append(prpCryptor.encrypt(row[i]))
                else:
                    try:
                        strRow.append(str(row[i]))
                    except:
                        strRow.append('byte data type')
            query_result_p.append(strRow)
    currentMenu='queryora'
    return render(request, 'queryora.html', locals())


#SQL审核必读
def dbaprinciples(request):
    context = {'currentMenu':'dbaprinciples'}
    return render(request, 'dbaprinciples.html', context)

#图表展示
def charts(request):
    context = {'currentMenu':'charts'}
    return render(request, 'charts.html', context)



#获取当前请求url
def _getDetailUrl(request):
    scheme = request.scheme
    #host = request.META['HTTP_HOST']
    host = getattr(settings,'WAN_HOST')
    return "%s://%s/detail/" % (scheme, host)


#展示数据库schema列表
def oradict(request):
    primaries = configMap['oracle'].objects.all().order_by('cluster_name')
    if len(primaries) == 0:
        context = {'errMsg': '目标数为0, 请查看后端是否没有配置数据库信息'}
        return render(request, 'error.html', context)

    #获取所有数据库名称
    listAllClusterName = [primary.cluster_name for primary in primaries]
    
    clusterName = request.GET.get('cluster_name')

    if clusterName:
        listSchema = daoMap['oracle'].getAllSchemaByCluster(clusterName)
        result = {'listSchema':listSchema}
        return HttpResponse(json.dumps(result), content_type='application/json')
    #dictAllClusterSchema = OrderedDict()
    ##获取主库地址:
    #for clusterName in listAllClusterName:

    #    listSchema = daoMap['oracle'].getAllSchemaByCluster(clusterName)
    #    dictAllClusterSchema[clusterName] = listSchema
    return render(request,'oradict.html',locals())

#个人中心
def myProfile(request):
    pass

#配置用户权限
@check_admin
def privConfig(request):
    after_range_num = 5
    before_range_num = 4
    try:
        page = int(request.GET.get('page','1'))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    listUsers = users.objects.filter(is_active=1).order_by('username')
    paginator = Paginator(listUsers, 10)
    listCluster = ora_primary_config.objects.all().order_by('cluster_name')
    try:
        listUsersP = paginator.page(page)
    except (EmptyPage,InvalidPage,PageNotAnInteger):
        listUsersP = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+before_range_num]
    else:
        page_range = paginator.page_range[0:int(page)+before_range_num]
    currentMenu='privconfig'
    return render(request,'privconfig.html',locals())

def myPrivs(request):
    listUsers = users.objects.filter(username=request.session.get('login_username'))
    listCluster = ora_primary_config.objects.all().order_by('cluster_name')
    currentMenu='myprivs'
    return render(request,'myprivs.html',locals())

def assignToMe(request):
    loginUser = request.session.get('login_username')
    workflowId = request.POST['workflowid']
    with transaction.atomic():
        try:
            workflowDetail = workflow.objects.select_for_update().get(id=workflowId,status=Const.workflowStatus['manexec'],operator=None)
        except Exception:
            context = {'errMsg': '获取工单状态失败或者已经有人在处理'}
            return render(request, 'error.html', context)
        try:
            reviewMen = json.loads(workflowDetail.review_man)
        except Exception:
            reviewMen = workflowDetail.review_man
        
        if not loginUser in reviewMen:
            context = {'errMsg': '你不在审核人之列'}
            return render(request, 'error.html', context)
        workflowDetail.operator = loginUser
        try:
            workflowDetail.save()
        except Exception as e:
            context = {'errMsg': str(e)}
            return render(request, 'error.html', context)
        else:
            return HttpResponseRedirect('/detail/' + str(workflowId) + '/') 
