from django.shortcuts import render
from .models import ora_awr_report
from sql.models import ora_primary_config,operation_ctl
from sql.views import check_admin
from .daoora import DaoOra
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.db.utils import IntegrityError
from .tasks import getAsignAwr,collectStat
import json
import math
import pdb

daoora=DaoOra()

# Create your views here.
@check_admin
def allAwr(request):
    primaries = ora_primary_config.objects.all()
    listAllClusterName = [primary.cluster_name for primary in primaries]
    clusterName = request.GET.get('cluster_name')
    snapId = request.GET.get('snap_id')
    awrName = request.GET.get('awr_name')
    op = request.GET.get('op')
    if clusterName and not snapId:
        pageLimit=10
        try:
            page = int(request.GET.get('page','1'))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        finalStatus,msg,headerList,resultList = daoora.getSnapshot(clusterName)
        if finalStatus!='执行结束':
            result={'status':'error','msg':msg}
            return HttpResponse(json.dumps(result), content_type='application/json')
        cnt=len(resultList)
        pages=math.ceil(cnt/pageLimit)
        hasAwr = ora_awr_report.objects.filter(cluster_name=clusterName)
        hasSnapDict={}
        for row in hasAwr:
            hasSnapDict[row.end_snap_id]=row.status
        after_range_num = 5
        before_range_num = 4
        snapList=[]
        for row in resultList:
            if row[0] in hasSnapDict.keys():
                snapList.append([row[0],row[1],hasSnapDict[row[0]]])
            else:
                snapList.append([row[0],row[1],'init'])
        snapList=snapList[pageLimit*page-pageLimit:pageLimit*page-1]
        #paginator = Paginator(snapList, 10)
        #try:
        #    listSnapshot = paginator.page(page)
        #except (EmptyPage,InvalidPage,PageNotAnInteger):
        #    listSnapshot = paginator.page(1)
        #if page >= after_range_num:
        #    page_range = paginator.page_range[page-after_range_num:page+before_range_num]
        #else:
        #    page_range = paginator.page_range[0:int(page)+before_range_num]
        result={'status':'ok','pages':pages,'list_snapshot':snapList}
        return HttpResponse(json.dumps(result), content_type='application/json')
    elif clusterName and snapId and op=='generate':
        awrObject=ora_awr_report(cluster_name=clusterName,end_snap_id=snapId)
        try:
            awrObject.save()
        except IntegrityError:
            result={'msg':'正在生成中或已生成完毕'}
            return HttpResponse(json.dumps(result), content_type='application/json')
        except Exception as err:
            result={msg:str(err)}
            return HttpResponse(json.dumps(result), content_type='application/json')
        else:
            getAsignAwr.delay(clusterName,snapId)
            result={'msg':'开始生成报告'}
            return HttpResponse(json.dumps(result), content_type='application/json')
    elif clusterName and snapId and op=='display':
        try:
            awrReport = ora_awr_report.objects.get(cluster_name=clusterName,end_snap_id=snapId)
        except Exception as err:
            context = {'errMsg':'报告还未生成!'}
            return render(request, 'error.html', context)
        if awrReport.status != 'generated':
            context = {'errMsg':'报告还未生成!'}
            return render(request, 'error.html', context)
        else:
            awrPath = awrReport.awr_location
            result={'awr_path':'/awrdisplay/?awrPath='+awrPath}
            return HttpResponse(json.dumps(result), content_type='application/json')
            #return HttpResponseRedirect('/awrdisplay/?awrPath='+awrPath)
    return render(request,'allawr.html',locals())

def awrDisplay(request):
    awrPath = request.GET.get('awrPath')
    return render(request,awrPath)

def generateSnap(request):
    clusterName = request.GET['cluster_name']
    msg=daoora.snapshot(clusterName)
    result={'msg':msg}
    return HttpResponse(json.dumps(result), content_type='application/json')

def statCollect(request):
    primaries = ora_primary_config.objects.all().order_by('cluster_name')
    listCluster = [primary.cluster_name for primary in primaries]
    clusterListCollect = request.POST.get('cluster_list_collect')
    if clusterListCollect:
        clusterListCollect=json.loads(clusterListCollect)
        ctl = operation_ctl.objects.get(data_type='统计信息' ,opt_type='收集')
        if ctl.status == '进行中':
            finalResult = {'status':'error','msg':'有任务进行中'}
        else:
            ctl.status='进行中'
            ctl.save()
            collectStat.delay(clusterListCollect)
            finalResult = {'status':'ok'}
        return HttpResponse(json.dumps(finalResult), content_type='application/json')
    finalResult = {'listCluster':listCluster}
    return HttpResponse(json.dumps(finalResult), content_type='application/json')
