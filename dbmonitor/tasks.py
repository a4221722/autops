# --* coding=utf-8 *--
import json
import threading

from .daoora import DaoOra
from celery import task
from .models import ora_awr_report

daoora=DaoOra()

@task()
def getAsignAwr(cluseterName,snapId):
    #report = ora_awr_report.objects.get(cluster_name=cluseterName,end_snap_id=snapId)
    daoora.getAwr(cluseterName,snapId)

@task()
def collectStat(clusterListCollect):
    ctl = operation_ctl.objects.get(data_type='统计信息' ,opt_type='收集')
    operationRecord = operation_record()
    operationRecord.data_type='统计信息'
    operationRecord.opt_type='收集'
    operationRecord.status='进行中'
    operationRecord.message=''
    operationRecord.save()
    threadList=[]
    for clusterName in clusterListCollect:
        operationRecord.message+='开始收集'+clusterName+'.$$'
        operationRecord.save()
        threadList.append(threading.Thread(target = daoora.collectStat,args=(clusterName)))
    for t in threadList:
        t.start()
        t.join()
        if t.get_result() != 'ok':
            operationRecord.status='有异常'
            operationRecord.message+=result+'$$'
            operationRecord.save()
            continue
        else:
            operationRecord.message+='收集完毕.$$'
            operationRecord.save()
            continue

    if operationRecord.status=='有异常':
        pass
    else:
        operationRecord.status='已结束'
    operationRecord.finish_time=getNow()
    operationRecord.message+=','.join(clusterResult)
    operationRecord.save()
    ctl.status='正常'
    ctl.save()


