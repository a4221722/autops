# --* coding=utf-8 *--
import json

from .daoora import DaoOra
from .getnow import getNow
from .models import operation_record,operation_ctl,ora_primary_config,ora_tables,workflow,users
from .const import Const
from celery import task
from django.db.utils import IntegrityError
from django.conf import settings
from .sendmail import MailSender
from .wechat import WechatAlert
from .dingtalk import dingAlert

daoora=DaoOra()
mailSender = MailSender()
wechatalert = WechatAlert()

from celery.signals import worker_process_init
from multiprocessing import current_process

@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

@task()
def syncDictData(clusterListSync):
    ctl = operation_ctl.objects.get(data_type='数据字典' ,opt_type='同步')
    operationRecord = operation_record()
    operationRecord.data_type='数据字典'
    operationRecord.opt_type='同步'
    operationRecord.status='进行中'
    operationRecord.message=''
    operationRecord.save()
    clusterResult = []
    for clusterName in clusterListSync:
        operationRecord.message+='开始同步'+clusterName+'.$$'
        operationRecord.save()
        primary = ora_primary_config.objects.get(cluster_name=clusterName)
        count = 0
        dictTime = primary.dict_time
        tableList = daoora.getAllTableByCluster(clusterName,dictTime.strftime("%Y-%m-%d %H:%M:%S"))
        if tableList and tableList[0] == 'error':
            operationRecord.status='有异常'
            operationRecord.message+=tableList[1]+'$$'
            operationRecord.save()
            continue
        #tabList = []
        if len(tableList) == 0:
            operationRecord.message+=clusterName+'不需要同步$$'
            operationRecord.save()
            continue
        for table in tableList:
            try:
                ora_tables(instance_id=primary.id,schema_name=table[0], table=table[1]).save()
            except IntegrityError:
                #operationRecord.message+=table[0]+'.'+table[1]+'已存在'+'$$'
                #operationRecord.save()
                continue
            except Exception as e:
                operationRecord.status='有异常'
                operationRecord.message+=(str(e))+'$$'
                operationRecord.save()
            else:
                #tabList.append(table[0]+'.'+table[1])
                count+=1
            #if count%50 == 0:
            #    operationRecord.message+=','.join(tabList)+'.$$'
            #    operationRecord.save
            #    tabList = []
        #operationRecord.message+=','.join(tabList)+'.$$'
        #operationRecord.save()
        clusterResult.append(clusterName+': '+str(count)+'张表同步成功')

        primary.dict_time = getNow()
        primary.save(keepPass=1)
        #finalResult['msg'] += clusterName+': '+str(count)+' 张表同步成功'+'<br/>'
    #return HttpResponse(json.dumps(finalResult), content_type='application/json')
    if operationRecord.status=='有异常':
        pass
    else:
        operationRecord.status='已结束'
    operationRecord.finish_time=getNow()
    operationRecord.message+=','.join(clusterResult)
    operationRecord.save()
    ctl.status='正常'
    ctl.save()

@task()
def oraAutoReview(workflowId):
    workflowDetail = workflow.objects.get(id=workflowId)
    sqlContent = workflowDetail.sql_content
    clusterNameStr = workflowDetail.cluster_name
    try:
        parseResult = daoora.sqlAutoreview(sqlContent,clusterNameStr)
    except Exception as err:
        workflowStatus = Const.workflowStatus['autoreviewwrong']
        jsonResult = json.dumps([{
            'clustername':workflowDetail.cluster_name,
            'id':1,
            'statge':'UNCHECKED',
            'errlevel':None,
            'stagestatus':'等待人工确认',
            'errormessage':str(err),
            'sql':workflowDetail.sql_content,
            'est_rows':0,
            'sequence':1,
            'backup_dbname':None,
            'execute_time':0,
            'real_rows':0}])
    else:
        jsonResult = json.dumps(parseResult)
        workflowStatus = Const.workflowStatus['manreviewing']
    
        for ret in parseResult:
            if ret['stage'] == 'UNCHECKED':
                workflowStatus = Const.workflowStatus['autoreviewwrong']
                break
    workflowDetail.review_content = jsonResult
    workflowDetail.status = workflowStatus
    workflowDetail.save()

#获取当前请求url
def _getDetailUrl(request):
    scheme = request.scheme
    #host = request.META['HTTP_HOST']
    host = getattr(settings,'WAN_HOST')
    return "%s://%s/detail/" % (scheme, host)

@task()
def mailDba(strTitle, strContent, emailList):
#如果进入等待人工审核状态了，则根据settings.py里的配置决定是否给审核人发一封邮件提醒.
    if hasattr(settings, 'MAIL_ON_OFF') == True:
        if getattr(settings, 'MAIL_ON_OFF') == "on":
                mailSender.sendEmail(strTitle, strContent, emailList)
        else:
            #不发邮件
            pass

@task()
def wechatDba(strTitle, strContent,user):
#如果开启微信通知，则发送微信
    if hasattr(settings, 'WECHAT_ON_OFF') == True and getattr(settings, 'WECHAT_ON_OFF') == "on":
        wechatalert.sendMessage(user, strTitle, strContent)

@task()
def dingDba(strContent,mobile):
#如果开启钉钉通知，则发送钉钉消息
    if hasattr(settings, 'DINGTALK_ON_OFF') == True and getattr(settings, 'DINGTALK_ON_OFF') == "on":
        dingAlert(strContent,mobile)
