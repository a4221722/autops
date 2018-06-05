# -*- coding: UTF-8 -*- 

import cx_Oracle
from django.conf import settings
from django.db import connection
from django.db.utils import IntegrityError
from sql.models import ora_primary_config
from .models import ora_awr_report
from sql.aes_decryptor import Prpcrypt
import datetime
import pdb
prpCryptor = Prpcrypt()

class DaoOra(object):

    def getDbInfo(self,clusterName):
        listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
        self.primaryHost = listPrimaries[0].primary_host
        self.primaryPort = listPrimaries[0].primary_port
        self.primarySrv = listPrimaries[0].primary_srv
        self.primaryUser = listPrimaries[0].primary_user
        self.primaryPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)
        self.charset = listPrimaries[0].charset

    def getStInfo(self,clusterName):
        listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
        self.standbyHost = listPrimaries[0].standby_host
        self.standbyPort = listPrimaries[0].standby_port
        self.standbySrv = listPrimaries[0].standby_srv
        self.standbyUser = listPrimaries[0].primary_user
        self.standbyPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)
        self.charset = listPrimaries[0].charset
    
    def getSnapshot(self,clusterName):
        self.getDbInfo(clusterName)
        finalStatus = '执行结束'
        msg = ''
        queryResult = []
        headerList = []
        oraLinkPr = self.primaryHost+':'+str(self.primaryPort)+'/'+self.primarySrv
        try:
            connPr = cx_Oracle.connect(self.primaryUser,self.primaryPassword,oraLinkPr,encoding=self.charset)
        except Exception as e:
            finalStatus = '数据库连接异常'
            msg = '数据库连接异常'
            return finalStatus,msg,headerList,queryResult
        else:
            crPr = connPr.cursor()
        sql="""select snap_id,to_char(end_interval_time, 'yyyymmdd hh24:mi') etim
            from dba_hist_snapshot 
            where instance_number = (select instance_number from v$instance) order by snap_id desc"""
        try:
            crPr.execute(sql)
        except Exception as e:
            finalStatus = '执行异常'
            msg = str(e)
        else:
            headerList = [row[0] for row in crPr.description]
            queryResult = crPr.fetchall()
        return finalStatus,msg,headerList,queryResult
    def getAwr(self,clusterName,snapId):
        awrObject=ora_awr_report.objects.get(cluster_name=clusterName,end_snap_id=snapId)
        awrObject.status='generating'
        awrObject.save()
        snapIdA = str(int(snapId)-1)
        snapId = str(snapId)
        self.getDbInfo(clusterName)
        oraLinkPr = self.primaryHost+':'+str(self.primaryPort)+'/'+self.primarySrv
        try:
            connPr = cx_Oracle.connect(self.primaryUser,self.primaryPassword,oraLinkPr,encoding=self.charset)
        except Exception as e:
            print(str(e))
        else:
            crPr = connPr.cursor()
        dbIdSql="select a.dbid,b.instance_number from v$database a,v$instance b"
        crPr.execute(dbIdSql)
        dbIdResult=crPr.fetchall()
        for dbId,instNum in dbIdResult:
            dbId=str(dbId)
            instNum=str(instNum)
            awrName = clusterName+'_'+snapId+'.html'
            intSql = """select * from(select snap_id, to_char(end_interval_time, 'yyyymmddhh24mi') etim, 
                    to_char(lag(end_interval_time, 1) over(order by snap_id),'yyyymmddhh24mi') btim
                    from dba_hist_snapshot
                    where instance_number ="""+instNum+") where snap_id="+snapId
            crPr.execute(intSql)
            interval = [str(row[2])+'-'+str(row[1]) for row in crPr.fetchall()]
            try:
                awrSql = "select output from table(dbms_workload_repository.awr_report_html("+dbId+','+instNum+','+snapIdA+','+snapId+',0))'
                crPr.execute(awrSql)
                awrResult=crPr.fetchall()
                f=open(settings.BASE_DIR+'/awr/'+awrName,'a')
                for row in awrResult:
                    content=row[0]
                    if not content:
                        content='\n'
                    f.write(content)
                f.close()
            except Exception as err:
                awrObject.status='error: '+str(err)[:50]
            else:
                awrObject.status='generated'
                awrObject.awr_location=awrName
        awrObject.interval=interval[0]
        awrObject.save()

