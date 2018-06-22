# --* coding=utf-8 *--
import json
from threading import Thread
import datetime

from .daoora import DaoOra
from .osinf import OsInf
from celery import task
from celery.schedules import crontab
from celery.decorators import periodic_task
from .models import ora_awr_report,os_host_config
from sql.models import operation_ctl,operation_record,ora_primary_config
from sql.getnow import getNow
from sql.aes_decryptor import Prpcrypt

daoora=DaoOra()
prpCryptor = Prpcrypt()

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

@periodic_task(run_every=30, name="probe_load_gen_snap", ignore_result=True)
def probeLoadGenSnap():
    hosts = os_host_config.objects.all()
    for host in hosts:
        osObj = OsInf(host.host_ip,host.host_user,prpCryptor.decrypt(host.host_password),host.host_port)
        value = float(osObj.getLoad())
        timeDelt = datetime.datetime.now() - host.update_time
        if (value >= 10 and host.snap_flag == 0)  or (value >= 10 and host.snap_flag == 1 and timeDelt.days*3600*24+timeDelt.seconds > 300):
            primaries = ora_primary_config.objects.filter(primary_host = host.host_ip)
            for primary in primaries:
                daoora.snapshot(primary.cluster_name)
            host.snap_flag = 1
            host.save(keepPass=1)
        elif value < 10 and host.snap_flag == 1:
            primaries = ora_primary_config.objects.filter(primary_host = host.host_ip)
            for primary in primaries:
                daoora.snapshot(primary.cluster_name)
            host.snap_flag = 0
            host.save(keepPass=1)


