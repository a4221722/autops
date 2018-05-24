# --* coding=utf-8 *--

from .daoora import DaoOra
from .getnow import getNow
from .models import operation_record,operation_ctl,ora_primary_config,ora_tables
from celery import task
from django.db.utils import IntegrityError

daoora=DaoOra()

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
                ora_tables(cluster_name=clusterName,schema_name=table[0], table=table[1]).save()
            except IntegrityError:
                operationRecord.message+=table[0]+'.'+table[1]+'已存在'+'$$'
                operationRecord.save()
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
    operationRecord.status='已结束'
    operationRecord.finish_time=getNow()
    operationRecord.message+=','.join(clusterResult)
    operationRecord.save()
    ctl.status='正常'
    ctl.save()
