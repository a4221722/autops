# --* coding=utf-8 *--
import json

from .daoora import DaoOra
from celery import task
from .models import ora_awr_report

daoora=DaoOra()

@task()
def getAsignAwr(cluseterName,snapId):
    report = ora_awr_report.objects.get(cluster_name=cluseterName,end_snap_id=snapId)
    daoora.getAwr(cluseterName,snapId)


