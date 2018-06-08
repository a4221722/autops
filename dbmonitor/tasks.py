# --* coding=utf-8 *--
import json
from threading import Thread

from .daoora import DaoOra
from celery import task
from .models import ora_awr_report
from sql.models import operation_ctl,operation_record
from sql.getnow import getNow

daoora=DaoOra()

class workThread(Thread):
    def __init__(self,func,args=()):
        super(workThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

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
        t=workThread(daoora.collectStat,(clusterName,))
        threadList.append(t)
        t.start()
    for t in threadList:
        t.join()
        result=t.get_result()
        if result != 'ok':
            operationRecord.status='有异常'
            operationRecord.message+=getNow()+' - '+result+'$$'
            operationRecord.save()
            continue
        else:
            operationRecord.message+=getNow()+' - '+'收集完毕.$$'
            operationRecord.save()
            continue

    if operationRecord.status=='有异常':
        pass
    else:
        operationRecord.status='已结束'
    operationRecord.finish_time=getNow()
    operationRecord.save()
    ctl.status='正常'
    ctl.save()


