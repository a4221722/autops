# -*- coding: UTF-8 -*- 

import re
import json
import datetime
import multiprocessing
import pdb

from django.db.models import Q
from django.db.utils import IntegrityError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
if settings.ENABLE_LDAP:
    from django_auth_ldap.backend import LDAPBackend

from .daoora import DaoOra
from .const import Const
from .aes_decryptor import Prpcrypt
from .models import users, workflow,ora_primary_config, ora_tables,ora_tab_privs,operation_ctl,operation_record
from sql.sendmail import MailSender
from .getnow import getNow
import logging
from sql.tasks import syncDictData

logger = logging.getLogger('default')
mailSender = MailSender()
daoora = DaoOra()
prpCryptor = Prpcrypt()
login_failure_counter = {} #登录失败锁定计数器，给loginAuthenticate用的
sqlSHA1_cache = {} #存储SQL文本与SHA1值的对应关系，尽量减少与数据库的交互次数,提高效率。格式: {工单ID1:{SQL内容1:sqlSHA1值1, SQL内容2:sqlSHA1值2},}

def log_mail_record(login_failed_message):
    mail_title = 'login inception'
    logger.warning(login_failed_message)
    mailSender.sendEmail(mail_title, login_failed_message, getattr(settings, 'MAIL_REVIEW_DBA_ADDR'))

#ajax接口，登录页面调用，用来验证用户名密码
@csrf_exempt
def loginAuthenticate(username, password):
    """登录认证，包含一个登录失败计数器，5分钟内连续失败5次的账号，会被锁定5分钟"""
    lockCntThreshold = settings.LOCK_CNT_THRESHOLD
    lockTimeThreshold = settings.LOCK_TIME_THRESHOLD

    #服务端二次验证参数
    strUsername = username
    strPassword = password

    if strUsername == "" or strPassword == "" or strUsername is None or strPassword is None:
        result = {'status':2, 'msg':'登录用户名或密码为空，请重新输入!', 'data':''}
    elif strUsername in login_failure_counter and login_failure_counter[strUsername]["cnt"] >= lockCntThreshold and (datetime.datetime.now() - login_failure_counter[strUsername]["last_failure_time"]).seconds <= lockTimeThreshold:
        log_mail_record('user:{},login failed, account locking...'.format(strUsername))
        result = {'status':3, 'msg':'登录失败超过5次，该账号已被锁定5分钟!', 'data':''}
    else:
        correct_users = users.objects.filter(username=strUsername)
        if len(correct_users) == 1 and correct_users[0].is_active and check_password(strPassword, correct_users[0].password) == True:
            #调用了django内置函数check_password函数检测输入的密码是否与django默认的PBKDF2算法相匹配
            if strUsername in login_failure_counter:
                #如果登录失败计数器中存在该用户名，则清除之
                login_failure_counter.pop(strUsername)
            result = {'status':0, 'msg':'ok', 'data':''}
        else:
            if strUsername not in login_failure_counter:
                #第一次登录失败，登录失败计数器中不存在该用户，则创建一个该用户的计数器
                login_failure_counter[strUsername] = {"cnt":1, "last_failure_time":datetime.datetime.now()}
            else:
                if (datetime.datetime.now() - login_failure_counter[strUsername]["last_failure_time"]).seconds <= lockTimeThreshold:
                    login_failure_counter[strUsername]["cnt"] += 1
                else:
                    #上一次登录失败时间早于5分钟前，则重新计数。以达到超过5分钟自动解锁的目的。
                    login_failure_counter[strUsername]["cnt"] = 1
                login_failure_counter[strUsername]["last_failure_time"] = datetime.datetime.now()
            if login_failure_counter[strUsername]["cnt"]%10==0:
                log_mail_record('user:{},login failed, fail count:{}'.format(strUsername,login_failure_counter[strUsername]["cnt"]))
            result = {'status':1, 'msg':'用户名或密码错误，请重新输入！', 'data':''}
    return result

#ajax接口，登录页面调用，用来验证用户名密码
@csrf_exempt
def authenticateEntry(request):
    """接收http请求，然后把请求中的用户名密码传给loginAuthenticate去验证"""
    if request.is_ajax():
        strUsername = request.POST.get('username')
        strPassword = request.POST.get('password')
    else:
        strUsername = request.POST['username']
        strPassword = request.POST['password']

    lockCntThreshold = settings.LOCK_CNT_THRESHOLD
    lockTimeThreshold = settings.LOCK_TIME_THRESHOLD

    if settings.ENABLE_LDAP:
        ldap = LDAPBackend()
        try:
            user = ldap.authenticate(username=strUsername, password=strPassword)
        except Exception as err:
            result = {'msg': 'ldap authorization failed'}
            return HttpResponse(json.dumps(result), content_type='application/json')

        if strUsername in login_failure_counter and login_failure_counter[strUsername]["cnt"] >= lockCntThreshold and (
            datetime.datetime.now() - login_failure_counter[strUsername][
            "last_failure_time"]).seconds <= lockTimeThreshold:
            log_mail_record('user:{},login failed, account locking...'.format(strUsername))
            result = {'status': 3, 'msg': '登录失败超过5次，该账号已被锁定5分钟!', 'data': ''}
            return HttpResponse(json.dumps(result), content_type='application/json')
        if user and user.is_active:
            request.session['login_username'] = strUsername
            result = {'status': 0, 'msg': 'ok', 'data': ''}
            return HttpResponse(json.dumps(result), content_type='application/json')

    result = loginAuthenticate(strUsername, strPassword)
    if result['status'] == 0:
        request.session['login_username'] = strUsername
    return HttpResponse(json.dumps(result), content_type='application/json')



#Oracle SQL简单审核
@csrf_exempt
def orasimplecheck(request):
    if request.is_ajax():
        sqlContent = request.POST.get('sql_content')
        clusterName = request.POST.get('cluster_name')
        
    else:
        sqlContent = request.POST['sql_content']
        clusterName = request.POST['cluster_name']
        
        
    finalResult = {'status':'ok', 'msg':'检测通过', 'data':[]}
    #服务器端参数验证
    if sqlContent is None or clusterName is None:
        finalResult['status'] = 'error'
        finalResult['msg'] = '页面提交参数可能为空'
        return HttpResponse(json.dumps(finalResult), content_type='application/json')

    sqlContent = sqlContent.rstrip()
    if sqlContent[-1] != ";":
        finalResult['status'] = 'error'
        finalResult['msg'] = 'Oracle SQL语句结尾没有以;结尾，请重新修改并提交！'
        return HttpResponse(json.dumps(finalResult), content_type='application/json')
    sqlContent = sqlContent.rstrip(';')
    #使用explain plan进行自动审核
    try:
        resultList = daoora.sqlAutoreview(sqlContent, clusterName)
    except Exception as err:
        finalResult['status'] = 'error'
        finalResult['msg'] = str(err)
    else:
        for result in resultList:
            if result['stage'] != 'CHECKED':
                finalResult['status'] = 'error'
                finalResult['msg'] = result['errormessage']+' -- '+result['sql']
                #return HttpResponse(json.dumps(finalResult), content_type='application/json')
    #要把result转成JSON存进数据库里，方便SQL单子详细信息展示
    return HttpResponse(json.dumps(finalResult), content_type='application/json')

#同步表数据字典
@csrf_exempt
def syncoradict(request):
    primaries = ora_primary_config.objects.all().order_by('cluster_name')
    listCluster = [primary.cluster_name for primary in primaries]
    clusterListSync = request.POST.get('cluster_list_sync')
    if clusterListSync:
        clusterListSync=json.loads(clusterListSync)
        ctl = operation_ctl.objects.get(data_type='数据字典' ,opt_type='同步')
        if ctl.status == '进行中':
            finalResult = {'status':'error','msg':'有任务进行中'}
        else:
            ctl.status='进行中'
            ctl.save()
            syncDictData.delay(clusterListSync)
            finalResult = {'status':'ok'}
        return HttpResponse(json.dumps(finalResult), content_type='application/json')
    finalResult = {'listCluster':listCluster}
    return HttpResponse(json.dumps(finalResult), content_type='application/json')


#同步ldap用户到数据库
@csrf_exempt
def syncldapuser(request):
    if not settings.ENABLE_LDAP:
        result = {'msg': 'LDAP支持未开启'}
        return HttpResponse(json.dumps(result), content_type='application/json')
    ldapback = LDAPBackend()
    ldap = ldapback.ldap
    ldapconn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    tls = getattr(settings, 'AUTH_LDAP_START_TLS', None)
    if tls:
        ldapconn.start_tls_s()
    binddn = settings.AUTH_LDAP_BIND_DN
    bind_password = settings.AUTH_LDAP_BIND_PASSWORD
    basedn = settings.AUTH_LDAP_BASEDN
    ldapconn.simple_bind_s(binddn, bind_password)
    ldapusers = ldapconn.search_s(basedn, ldap.SCOPE_SUBTREE, 'objectclass=*', attrlist=settings.AUTH_LDAP_USER_ATTRLIST)
    #ldap中username存在条目的第一个元素的uid中，定义的username_field不再使用，改为截取user_tag
    #username_field = settings.AUTH_LDAP_USER_ATTR_MAP['username']
    display_field = settings.AUTH_LDAP_USER_ATTR_MAP['display']
    email_field = settings.AUTH_LDAP_USER_ATTR_MAP['email']
    count = 0
    try:
        for user in ldapusers:
            user_tag=user[0].split(',')
            user_attr = user[1]
            if user_tag and user_attr:
                username = user_tag[0][user_tag[0].find('=')+1:].encode()
                display = user_attr.get(display_field,['none'.encode(),])[0]
                email = user_attr.get(email_field,['none'.encode(),])[0]
                already_user = users.objects.filter(username=username.decode()).filter(is_ldapuser=True)
                if len(already_user) == 0:
                    u = users(username=username.decode(), display=display.decode(), email=email.decode(), is_ldapuser=True,is_active=0)
                    u.save()
                    count += 1
    except Exception as err:
        result = {'msg': '用户{0}导入错误:{1}'.format(username,str(err))}
        return HttpResponse(json.dumps(result))
    else:
        result = {'msg': '同步{}个用户.'.format(count)}
        return HttpResponse(json.dumps(result), content_type='application/json')

#请求图表数据
@csrf_exempt
def getMonthCharts(request):
    result = daoora.getWorkChartsByMonth()
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def getPersonCharts(request):
    result = daoora.getWorkChartsByPerson()
    return HttpResponse(json.dumps(result), content_type='application/json')

def getSqlSHA1(workflowId):
    """调用django ORM从数据库里查出review_content，从其中获取sqlSHA1值"""
    workflowDetail = get_object_or_404(workflow, pk=workflowId)
    dictSHA1 = {}
    # 使用json.loads方法，把review_content从str转成list,
    listReCheckResult = json.loads(workflowDetail.review_content)

    for rownum in range(len(listReCheckResult)):
        id = rownum + 1
        sqlSHA1 = listReCheckResult[rownum][10]
        if sqlSHA1 != '':
            dictSHA1[id] = sqlSHA1

    if dictSHA1 != {}:
        # 如果找到有sqlSHA1值，说明是通过pt-OSC操作的，将其放入缓存。
        # 因为使用OSC执行的SQL占较少数，所以不设置缓存过期时间
        sqlSHA1_cache[workflowId] = dictSHA1
    return dictSHA1

@csrf_exempt
def getOscPercent(request):
    """获取该SQL的pt-OSC执行进度和剩余时间"""
    workflowId = request.POST['workflowid']
    sqlID = request.POST['sqlID']
    if workflowId == '' or workflowId is None or sqlID == '' or sqlID is None:
        context = {"status":-1 ,'msg': 'workflowId或sqlID参数为空.', "data":""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    sqlID = int(sqlID)
    dictSHA1 = {}
    if workflowId in sqlSHA1_cache:
        dictSHA1 = sqlSHA1_cache[workflowId]
        # cachehit = "已命中"
    else:
        dictSHA1 = getSqlSHA1(workflowId)

    if dictSHA1 != {} and sqlID in dictSHA1:
        sqlSHA1 = dictSHA1[sqlID]
        result = inceptionDao.getOscPercent(sqlSHA1)  #成功获取到SHA1值，去inception里面查询进度
        if result["status"] == 0:
            # 获取到进度值
            pctResult = result
        else:
            # result["status"] == 1, 未获取到进度值,需要与workflow.execute_result对比，来判断是已经执行过了，还是还未执行
            execute_result = workflow.objects.get(id=workflowId).execute_result
            try:
                listExecResult = json.loads(execute_result)
            except ValueError:
                listExecResult = execute_result
            if type(listExecResult) == list and len(listExecResult) >= sqlID-1:
                if dictSHA1[sqlID] in listExecResult[sqlID-1][10]:
                    # 已经执行完毕，进度值置为100
                    pctResult = {"status":0, "msg":"ok", "data":{"percent":100, "timeRemained":""}}
            else:
                # 可能因为前一条SQL是DML，正在执行中；或者还没执行到这一行。但是status返回的是4，而当前SQL实际上还未开始执行。这里建议前端进行重试
                pctResult = {"status":-3, "msg":"进度未知", "data":{"percent":-100, "timeRemained":""}}
    elif dictSHA1 != {} and sqlID not in dictSHA1:
        pctResult = {"status":4, "msg":"该行SQL不是由pt-OSC执行的", "data":""}
    else:
        pctResult = {"status":-2, "msg":"整个工单不由pt-OSC执行", "data":""}
    return HttpResponse(json.dumps(pctResult), content_type='application/json')

@csrf_exempt
def getWorkflowStatus(request):
    """获取某个工单的当前状态"""
    workflowId = request.POST['workflowid']
    if workflowId == '' or workflowId is None :
        context = {"status":-1 ,'msg': 'workflowId参数为空.', "data":""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    workflowDetail = get_object_or_404(workflow, pk=workflowId)
    workflowStatus = workflowDetail.status
    result = {"status":workflowStatus, "msg":"", "data":""}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def stopOscProgress(request):
    """中止该SQL的pt-OSC进程"""
    workflowId = request.POST['workflowid']
    sqlID = request.POST['sqlID']
    if workflowId == '' or workflowId is None or sqlID == '' or sqlID is None:
        context = {"status":-1 ,'msg': 'workflowId或sqlID参数为空.', "data":""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    loginUser = request.session.get('login_username', False)
    workflowDetail = workflow.objects.get(id=workflowId)
    try:
        listAllReviewMen = json.loads(workflowDetail.review_man)
    except ValueError:
        listAllReviewMen = (workflowDetail.review_man, )
    #服务器端二次验证，当前工单状态必须为等待人工审核,正在执行人工审核动作的当前登录用户必须为审核人. 避免攻击或被接口测试工具强行绕过
    if workflowDetail.status != Const.workflowStatus['executing']:
        context = {"status":-1, "msg":'当前工单状态不是"执行中"，请刷新当前页面！', "data":""}
        return HttpResponse(json.dumps(context), content_type='application/json')
    if loginUser is None or loginUser not in listAllReviewMen:
        context = {"status":-1 ,'msg': '当前登录用户不是审核人，请重新登录.', "data":""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    sqlID = int(sqlID)
    if workflowId in sqlSHA1_cache:
        dictSHA1 = sqlSHA1_cache[workflowId]
    else:
        dictSHA1 = getSqlSHA1(workflowId)
    if dictSHA1 != {} and sqlID in dictSHA1:
        sqlSHA1 = dictSHA1[sqlID]
        optResult = inceptionDao.stopOscProgress(sqlSHA1)
    else:
        optResult = {"status":4, "msg":"不是由pt-OSC执行的", "data":""}
    return HttpRespense(json.dumps(optResult), content_type='application/json')

@csrf_exempt
def manExec(request):
    workflowId = request.POST['workflowid']
    workflowDetail = workflow.objects.get(id=workflowId)
    workflowDetail.status = Const.workflowStatus['manexec']
    try:
        workflowDetail.save()
    except Exception as e:
        status = -1
        msg = str(e)
    else:
        status = 2
        msg = '更改状态为手工执行'
    result = {"status":status,"msg":msg}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def manFinish(request):
    workflowId = request.POST['workflowid']
    executeStatus = request.POST['status']
    executeResult = request.POST['content']
    workflowDetail = workflow.objects.get(id=workflowId)
    workflowDetail.execute_result = executeResult
    if executeStatus == '0':
        workflowDetail.status = Const.workflowStatus['manexcept']
    elif executeStatus == '1':
        workflowDetail.status = Const.workflowStatus['manfinish']

    try:
        workflowDetail.finish_time = getNow()
        workflowDetail.save()
    except Exception as e:
        status = -1
        msg = str(e)
    else:
        status = 2
        msg = '保存成功'
    result = {"status":status,"msg":msg}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def privMod(request,operation):
    loginUser = request.session.get('login_username', False)
    if loginUser != 'admin':
        context = {'errMsg': '无权限访问该页面'}
        return render(request, 'error.html', context)

    hasTableId = [tab.table_id for tab in ora_tab_privs.objects.filter(username = request.GET.get('username'))]
    if operation == 'add':
        tables = ora_tables.objects.all().exclude(id__in=hasTableId)
    elif operation == 'delete':
        tables =  ora_tables.objects.all().filter(id__in=hasTableId)
    clusterName = request.GET.get('cluster_name')
    schema = request.GET.get('schema')
    cluster_list = []
    schema_list = []
    table_list = []
    table_dict = {}
    if not clusterName and not schema:
        cluster_list = [primary.cluster_name for primary in ora_primary_config.objects.all()]
        cluster_list.sort()
    elif clusterName and not schema:
        instanceId = ora_primary_config.objects.get(cluster_name=clusterName).id
        schema_list = list(set([table.schema_name for table in tables.filter(instance_id=instanceId)]))
        schema_list.sort()
    elif clusterName and  schema:
        instanceId = ora_primary_config.objects.get(cluster_name=clusterName).id
        table_list = [table.table for table in tables.filter(instance_id=instanceId).filter(schema_name=schema)]
        table_dict = {}
        for table in tables.filter(instance_id=instanceId).filter(schema_name=schema).order_by('table'):
            table_dict[table.id] = table.table


    result = {'cluster_list':cluster_list,'schema_list':schema_list,'table_list':table_dict}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def privCommit(request,operation):
    loginUser = request.session.get('login_username', False)
    if loginUser != 'admin':
        context = {'errMsg': '无权限访问该页面'}
        return render(request, 'error.html', context)
    username = request.POST.get('username')
    table_list = request.POST.get('table_list')
    if table_list:
        tabList = json.loads(table_list)
    else:
        status = 'error'
        msg = '选择为空'
        result = {'status':status,'msg':msg}
        return HttpResponse(json.dumps(result), content_type='application/json')
    extra_inst_list = request.POST.get('extra_inst_list')
    if extra_inst_list:
        extraInstList = json.loads(extra_inst_list)
    #if len(extraInstList) > 0:
        oriTabList = tabList
        for extraInst in extraInstList:
            for i in range(0,len(oriTabList)):
                table_id = oriTabList[i]
                oraTab = ora_tables.objects.get(id = int(table_id))
                instance_id = ora_primary_config.objects.get(cluster_name=extraInst).id
                try:
                    extraId = ora_tables.objects.get(instance_id = instance_id,schema_name=oraTab.schema_name,table=oraTab.table).id
                except Exception as err:
                    pass
                else:
                    tabList.append(extraId)
    status = 'saved'
    msg = '保存成功'
    for table_id in tabList:
        try:
            if operation == 'add':
                p = ora_tab_privs.objects.filter(username = username,table = ora_tables(id = int(table_id)))
                if p.count() != 0:
                    status = 'save failed'
                    msg = '请勿重复保存'
                else:
                    ora_tab_privs(username = username,table = ora_tables(id = int(table_id))).save()
            elif operation == 'delete':
                p = ora_tab_privs.objects.filter(username = username,table = ora_tables(id = int(table_id)))
                if len(p) == 0:
                    status = 'save failed'
                    msg = '请勿重复删除'
                else:
                    p.delete()
        except IntegrityError:
            status = 'save failed'
            msg = '请勿重复保存'
        except Exception as e:
            print(str(e))
            status = 'save failed'
            msg = '有数据保存/删除失败'
        else:
            continue
    result = {'status':status,'msg':msg}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def getResult(request):
    logon_user = request.session.get('login_username', False)
    clusterName = request.POST.get('cluster_name')
    sqlContent = request.POST.get('sql_content')

    finalStatus,msg,headerList,queryResult = daoora.query(logon_user,clusterName,sqlContent)
    paginator = Paginator(queryResult, 10)
    after_range_num = 5
    before_range_num = 4
    try:
        page = int(request.GET.get('page','1'))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    try:
        queryResultP = paginator.page(page)
    except (EmptyPage,InvalidPage,PageNotAnInteger):
        queryResultP = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+before_range_num]
    else:
        page_range = paginator.page_range[0:int(page)+before_range_num]
    result = {'final_status':finalStatus,'msg':msg,'header_list':headerList,'query_result':queryResultP}
    return HttpResponse(locals(), content_type='application/json')
