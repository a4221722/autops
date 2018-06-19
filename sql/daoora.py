# -*- coding: UTF-8 -*- 

import cx_Oracle

from django.db import connection
from .models import ora_primary_config,ora_tab_privs,users,ora_tables
from .aes_decryptor import Prpcrypt
import datetime
import re
import json
import pdb
prpCryptor = Prpcrypt()
commentPattern = re.compile(r'^.*((--)|(/\*.*\*/)).*$',re.DOTALL)
selUdpPattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*(select).+for.+update.*$',re.DOTALL)
selPattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*(select).+$',re.DOTALL)
inselPattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*insert\s+into\s*(\S+\.{1}\S+).*(select.+)(from.+)$',re.DOTALL)
invalPattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*insert\s+into\s+(\S+\.{1}\S+).*values.+$',re.DOTALL)
updatePattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*update\s+(\S+\.{1}\S+.+)set\s+.+?(where.+)$',re.DOTALL)
ddlPattern = re.compile(r'^\s*((--.*\n+)|(/\*.*\*/))*\s*((create\s+(table|sequence|index))|(alter\s+(table|sequence|index))|(comment\s+on\s+(table|column)))\s+(\S+\.{1}\S+).+$',re.DOTALL)
descPattern = re.compile(r'^\s*desc\s+(\S+\.{1}\S+)\s*$')
showIndPattern = re.compile(r'^\s*show\s+index\s+from\s+(\S+\.{1}\S+)\s*$')
_CHART_DAYS = 90

__all__ = ('getAllSchemaByCluster','getAllTableByCluster','getWorkChartsByMonth','getWorkChartsByPerson','sqlAutoreview','executeFinal','query')

class DaoOra(object):

    def getDbInfo(self,clusterName):
        listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
        self.primaryHost = listPrimaries[0].primary_host
        self.primaryPort = listPrimaries[0].primary_port
        self.primarySrv = listPrimaries[0].primary_srv
        self.primaryUser = listPrimaries[0].primary_user
        self.primaryPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)
        self.charset = listPrimaries[0].charset
        self.primaryId = listPrimaries[0].id

    def getStInfo(self,clusterName):
        listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
        self.standbyHost = listPrimaries[0].standby_host
        self.standbyPort = listPrimaries[0].standby_port
        self.standbySrv = listPrimaries[0].standby_srv
        self.standbyUser = listPrimaries[0].primary_user
        self.standbyPassword = prpCryptor.decrypt(listPrimaries[0].primary_password)
        self.charset = listPrimaries[0].charset
        self.standbyId = listPrimaries[0].id

    #连进指定的Oracle实例里，读取所有schemas并返回
    def getAllSchemaByCluster(self,clusterName):
        self.getDbInfo(clusterName)
        listSchema = []
        conn = None
        cursor = None
        
        try:
            oraLink = self.primaryHost+':'+str(self.primaryPort)+'/'+self.primarySrv
            conn=cx_Oracle.connect(self.primaryUser,self.primaryPassword,oraLink,encoding=self.charset)
            cursor = conn.cursor()
           # sql="select value from v$parameter where name='service_names'"
            sql = """select username from dba_users where username not in ('SYSTEM',
                       'WMSYS',
                       'XDB',
                       'SYS',
                       'SCOTT',
                       'QMONITOR',
                       'OUTLN',
                       'ORDSYS',
                       'ORDDATA',
                       'OJVMSYS',
                       'MDSYS',
                       'LBACSYS',
                       'DVSYS',
                       'DBSNMP','APEX_040200','AUDSYS','CTXSYS','APEX_030200','EXFSYS','OLAPSYS','SYSMAN','WH_SYNC','GSMADMIN_INTERNAL','SI_INFORMTN_SCHEMA','MGMT_VIEW','OWBSYS','APEX_PUBLIC_USER','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','DIP','ANONYMOUS','MDDATA','OWBSYS_AUDIT','XS$NULL','APPQOSSYS','ORACLE_OCM','FLOWS_FILES','ORDPLUGINS','SYSBACKUP','SYSDG','SYSKM','GSMUSER') order by username"""
            n = cursor.execute(sql)
            listSchema = [row[0] for row in cursor.fetchall()]
        except cx_Oracle.Error as e:
            listSchema = ['数据库连接异常',]
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.commit()
                conn.close()
        return listSchema

    #连进指定的Oracle实例里，读取所有表名并返回
    def getAllTableByCluster(self, clusterName,dict_time=None):
        self.getDbInfo(clusterName)
        listTable = []
        conn = None
        cursor = None
        createFilter = ''
        if dict_time:
            createFilter = """ and (owner,table_name) in (select owner,object_name from dba_objects where object_type='TABLE' and created>=to_date('"""+dict_time+"""','yyyy-mm-dd hh24:mi:ss')) """
        try:
            oraLink = self.primaryHost+':'+str(self.primaryPort)+'/'+self.primarySrv
            conn=cx_Oracle.connect(self.primaryUser,self.primaryPassword,oraLink,encoding=self.charset)
            cursor = conn.cursor()
            sql = """select lower(owner),lower(table_name) from dba_tables where owner not in ('SYSTEM',
                       'WMSYS',
                       'XDB',
                       'SYS',
                       'SCOTT',
                       'QMONITOR',
                       'OUTLN',
                       'ORDSYS',
                       'ORDDATA',
                       'OJVMSYS',
                       'MDSYS',
                       'LBACSYS',
                       'DVSYS',
                       'DBSNMP','APEX_040200','AUDSYS','CTXSYS','APEX_030200','EXFSYS','OLAPSYS','SYSMAN','WH_SYNC','GSMADMIN_INTERNAL','SI_INFORMTN_SCHEMA','MGMT_VIEW','OWBSYS','APEX_PUBLIC_USER','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','DIP','ANONYMOUS','MDDATA','OWBSYS_AUDIT','XS$NULL','APPQOSSYS','ORACLE_OCM','FLOWS_FILES','ORDPLUGINS','SYSBACKUP','SYSDG','SYSKM','GSMUSER')""" + createFilter +" order by owner,table_name "
            n = cursor.execute(sql)
            listTable = [row for row in cursor.fetchall()]
        except cx_Oracle.Error as e:
            listTable = ['error',clusterName+': '+str(e)]
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
            return listTable

    def getWorkChartsByMonth(self):
        cursor = connection.cursor()
        sql = "select DATE_FORMAT(create_time,'%Y-%m-%d'),count(*) from sql_workflow where create_time>=SUBDATE(now(), INTERVAL {} DAY) group by DATE_FORMAT(create_time,'%Y-%m-%d')  order by 1 asc" .format(_CHART_DAYS)
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except Exception as e:
            print(str(e))
        return result

    def getWorkChartsByPerson(self):
        cursor = connection.cursor()
        sql = "select engineer, count(*) as cnt from sql_workflow where create_time>=SUBDATE(now(), INTERVAL {} DAY) group by engineer order by cnt desc limit 50".format(_CHART_DAYS)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def sqlAutoreview(self,sqlContent,clusterNameStr):
        clusterNameList = clusterNameStr.split(',')
        resultList=[]
        for clusterName in clusterNameList:
            listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
            primaryHost=listPrimaries[0].primary_host
            primaryPort=listPrimaries[0].primary_port
            primarySrv=listPrimaries[0].primary_srv
            primaryUser=listPrimaries[0].primary_user
            primaryPassword=prpCryptor.decrypt(listPrimaries[0].primary_password)
            oraLink = primaryHost+':'+str(primaryPort)+'/'+primarySrv
            try:
                conn=cx_Oracle.connect(primaryUser,primaryPassword,oraLink,encoding='gbk')
            except cx_Oracle.Error as e:
                #resultList.append([1,'UNCHECKED',0,'Server connected error: ',str(e),None,0,'0_0_1','test',0,0])
                resultList.append(
                {
                    'clustername':clusterName,
                    'id':1,
                    'stage':'UNCHECKED',
                    'errlevel':0,
                    'stagestatus':'Server connected error',
                    'errormessage':str(e)+': '+clusterName,
                    'sql':'',
                    'est_rows':0,
                    'sequence':None,
                    'backup_dbname':None,
                    'execute_time':0,
                    'real_rows':0})
                continue
            else:
                cursor = conn.cursor()
            sqlList = sqlContent.rstrip(';').replace('\r\n','\n').split(';')
            lastSql = ''
            cntId = 1
            for i in range(0,len(sqlList)):
                RESULT_DICT = {
                    'clustername':None,
                    'id':cntId,
                    'stage':None,
                    'errlevel':0,
                    'stagestatus':None,
                    'errormessage':None,
                    'sql':None,
                    'est_rows':0,
                    'sequence':None,
                    'backup_dbname':None,
                    'execute_time':0,
                    'real_rows':0}
                sql = lastSql+sqlList[i]
                cntSemi = sql.count("'")
                if cntSemi % 2 != 0:
                    lastSql+= sql+';'
                    continue
                else:
                    lastSql = ''
                sql = sql.strip()
                if invalPattern.match(sql.lower()):
                    rowsAffected = 1
                elif inselPattern.match(sql.lower()):
                    matchResult=inselPattern.match(sql.lower())
                    estSql = 'select count(*) '+matchResult[4]
                    cursor.execute(estSql)
                    for row in cursor:
                        rowsAffected=row[0]
                elif updatePattern.match(sql.lower()):
                    matchResult=updatePattern.match(sql.lower())
                    estSql = 'select count(*) from '+matchResult.group(4)+' '+matchResult.group(5)
                    cursor.execute(estSql)
                    for row in cursor:
                        rowsAffected=row[0]
                elif selPattern.match(sql.lower()):
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=cntId
                    RESULT_DICT['stage']='UNCHECKED'
                    RESULT_DICT['stagestatus']='解析失败'
                    RESULT_DICT['errormessage']="本页面不支持select操作"
                    RESULT_DICT['sql']=sql
                    resultList.append(RESULT_DICT)
                    #resultList.append([1,'CHECKED',0,'parse error: ',"don't support select statement",sql,0,'0_0_1','test',0,0])
                    continue
                elif ddlPattern.match(sql.lower()):
                    rowsAffected=0
                else:
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=1
                    RESULT_DICT['stage']='UNCHECKED'
                    RESULT_DICT['stagestatus']='解析失败'
                    RESULT_DICT['errormessage']="解析失败.请检查语法,查看sql审核必读后联系dba"
                    RESULT_DICT['sql']=sql
                    resultList.append(RESULT_DICT)
                    #resultList.append([1,'CHECKED',0,'parsed error: ',"unsupported statement, contact DBA ",sql,0,'0_0_1','test',0,0])
                    continue
                epsql = 'explain plan for '+sql
                try:
                    cursor.execute(epsql)
                except cx_Oracle.Error as e:
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=cntId
                    RESULT_DICT['stage']='UNCHECKED'
                    RESULT_DICT['stagestatus']='解析失败'
                    RESULT_DICT['errormessage']="解析失败,请确认语法,查看sql审核必读后联系dba"
                    RESULT_DICT['sql']=sql
                    resultList.append(RESULT_DICT)
                    #resultList.append([1,'CHECKED',0,'parsed error: ',str(e),sql,0,'0_0_1','test',0,0])
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return resultList
                else:
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=cntId
                    RESULT_DICT['stage']='CHECKED'
                    RESULT_DICT['stagestatus']='解析通过'
                    RESULT_DICT['sql']=sql
                    RESULT_DICT['est_rows']=rowsAffected
                    RESULT_DICT['errormessage']="解析通过"
                    resultList.append(RESULT_DICT)
                    cntId += 1
                    #resultList.append([1,'CHECKED',0,'parse completed','parse compeleted',sql,rowsAffected,'0_0_1','test',0,0])
            cursor.close()
            conn.close()
        return resultList
    
    def executeFinal(self, workflowDetail):
        '''
        连接数据库执行sql语句，返回结果
        '''
        clusterNameList = workflowDetail.cluster_name.split(',')
        reviewContent = json.loads(workflowDetail.review_content)
        resultList=[]
        finalStatus = '已正常结束'
        for clusterName in clusterNameList:
            clusterStatus = '已正常结束'
            listPrimaries = ora_primary_config.objects.filter(cluster_name=clusterName)
            primaryHost=listPrimaries[0].primary_host
            primaryPort=listPrimaries[0].primary_port
            primarySrv=listPrimaries[0].primary_srv
            primaryUser=listPrimaries[0].primary_user
            primaryPassword=prpCryptor.decrypt(listPrimaries[0].primary_password)
            primaryCharset=listPrimaries[0].charset
            oraLink = primaryHost+':'+str(primaryPort)+'/'+primarySrv
            try:
                conn=cx_Oracle.connect(primaryUser,primaryPassword,oraLink,encoding=primaryCharset)
            except Exception as e:
                finalStatus = '执行有异常'
                clusterStatus = '执行有异常'
                resultList.append(
                     {
                        'clustername':clusterName,
                        'id':1,
                        'stage':'UNEXECUTED',
                        'errlevel':0,
                        'stagestatus':'连接服务器异常',
                        'errormessage':str(e),
                        'sql':'',
                        'est_rows':0,
                        'sequence':None,
                        'backup_dbname':None,
                        'execute_time':0,
                        'real_rows':0})
                #resultList.append([1,'UNCHECKED',0,'Server connected error: '+e,None,sql,0,'0_0_1','test',0,0])
                continue
            else:
                cursor = conn.cursor()
            sqlList=workflowDetail.sql_content.rstrip(';').split(';')
            #sqlList = sqlContent.rstrip(';').split(';')
            lastSql = ''
            cntId=1
            for i in range(0,len(sqlList)):
                RESULT_DICT = {
                    'clustername':None,
                    'id':1,
                    'stage':None,
                    'errlevel':0,
                    'stagestatus':None,
                    'errormessage':'',
                    'sql':'',
                    'est_rows':0,
                    'sequence':None,
                    'backup_dbname':None,
                    'execute_time':0,
                    'real_rows':0}
                sql = lastSql+sqlList[i]
                cntSemi = sql.count("'")
                if cntSemi % 2 != 0:
                    lastSql+= sql+';'
                    continue
                else:
                    lastSql = ''
                try:
                    startTime=datetime.datetime.now()
                    cursor.execute(sql)
                except cx_Oracle.Error as e:
                    finalStatus = '执行有异常'
                    clusterStatus = '执行有异常'
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=cntId
                    RESULT_DICT['stage']='UNEXECUTED'
                    RESULT_DICT['stagestatus']='sql执行异常'
                    RESULT_DICT['sql']=sql
                    RESULT_DICT['execute_time']=round((datetime.datetime.now()-startTime).microseconds/1000)
                    RESULT_DICT['errormessage']=str(e)
                    resultList.append(RESULT_DICT)
                    #resultList.append([1,'EXECUTED',0,'execution error',str(e),content[5],content[6],'0_0_1','test',round((datetime.datetime.now()-startTime).microseconds/1000),0])
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    break
                else:
                    rowsReal = cursor.rowcount
                    RESULT_DICT['clustername']=clusterName
                    RESULT_DICT['id']=cntId
                    RESULT_DICT['stage']='EXECUTED'
                    RESULT_DICT['stagestatus']='sql执行完毕'
                    RESULT_DICT['sql']=sql
                    RESULT_DICT['execute_time']=round((datetime.datetime.now()-startTime).microseconds/1000)
                    RESULT_DICT['real_rows']=rowsReal
                    RESULT_DICT['est_rows']=reviewContent[cntId-1]['est_rows']
                    resultList.append(RESULT_DICT)
                    cntId+=1
                    #resultList.append([1,'EXECUTED',0,'execution complete','ok',content[5],content[6],'0_0_1','test',round((datetime.datetime.now()-startTime).microseconds/1000),rowsReal])
            if clusterStatus == '已正常结束':
                conn.commit()
                cursor.close()
                conn.close()
        return finalStatus,resultList

    #执行查询语句
    def query(self,logon_user,clusterName,sqlContent):
        self.getDbInfo(clusterName)
        self.getStInfo(clusterName)
        oraLinkPr = self.primaryHost+':'+str(self.primaryPort)+'/'+self.primarySrv
        oraLink = self.standbyHost+':'+str(self.standbyPort)+'/'+self.standbySrv
        finalStatus = '执行结束'
        msg = ''
        queryResult = []
        headerList = []
        #正则匹配判断是否是select或者desc操作
        if selPattern.match(sqlContent.lower()) and selUdpPattern.match(sqlContent.lower()):
            finalStatus = '不支持的操作'
            msg = "不支持select for update操作"
        elif selPattern.match(sqlContent.lower()) or descPattern.match(sqlContent.lower()) or showIndPattern.match(sqlContent.lower()):
            try:
                connPr = cx_Oracle.connect(self.primaryUser,self.primaryPassword,oraLinkPr,encoding=self.charset)
                conn = cx_Oracle.connect(self.standbyUser,self.standbyPassword,oraLink,encoding=self.charset)
            except Exception as e:
                finalStatus = '数据库连接异常'
                msg = '数据库连接异常'
                return finalStatus,msg,headerList,queryResult
            else:
                crPr = connPr.cursor()
                cr = conn.cursor()
            #select操作获取执行计划
            if selPattern.match(sqlContent.lower()):
                epsql = 'explain plan for '+sqlContent
                try:
                    crPr.execute(epsql)
                except Exception as e:
                    finalStatus = '解析失败'
                    msg = str(e)
                    return finalStatus,msg,headerList,queryResult
                crPr.execute("""select distinct a.object_owner,
                    (case
                      when a.object_type='TABLE' then
                       a.object_name
                      when a.object_type like 'INDEX%' then
                       d.table_name
                      else
                       null
                    end) tab
  	            from plan_table a,
                    dba_tables c,
                    dba_indexes d
                    where a.object_name = c.table_name(+)
                       and a.object_owner = c.OWNER(+)
                       and a.object_name = d.index_name(+)
                       and a.object_owner = d.OWNER(+)""" )
                eqResult = crPr.fetchall()
                if len(eqResult) <= 2 and (row[1] is None for row in eqResult):
                    sqlContent = sqlContent
                else:
                    sqlContent = 'select * from ('+sqlContent+') where rownum <= 200'
            elif descPattern.match(sqlContent.lower()):
                mt=descPattern.match(sqlContent.lower())
                mts = mt.group(1).split('.')
                eqResult = [mts,]
                sqlContent= """SELECT --OWNER,
                                    --TABLE_NAME,
                                    COLUMN_NAME,
                                    DATA_TYPE
                                    || DECODE (
                                          DATA_TYPE,
                                          'NUMBER', DECODE (
                                                          '('
                                                       || NVL (TO_CHAR (DATA_PRECISION), '*')
                                                       || ','
                                                       || NVL (TO_CHAR (DATA_SCALE), '*')
                                                       || ')',
                                                       '(*,*)', NULL,
                                                       '(*,0)', '(38)',
                                                          '('
                                                       || NVL (TO_CHAR (DATA_PRECISION), '*')
                                                       || ','
                                                       || NVL (TO_CHAR (DATA_SCALE), '*')
                                                       || ')'),
                                          'FLOAT', '(' || DATA_PRECISION || ')',
                                          'DATE', NULL,
                                          'TIMESTAMP(6)', NULL,
                                          '(' || DATA_LENGTH || ')')
                                       AS DATA_TYPE,
                                    NULLABLE
                               FROM DBA_TAB_COLUMNS
                              WHERE OWNER IN (upper('"""+mts[0]+"""'))
                                    AND TABLE_NAME = UPPER ('"""+mts[1]+"""')
                            ORDER BY OWNER, TABLE_NAME, COLUMN_ID"""
            elif showIndPattern.match(sqlContent.lower()):
                mt=showIndPattern.match(sqlContent.lower())
                mts = mt.group(1).split('.')
                eqResult = [mts,]
                sqlContent= """select a.index_Name,
                                listagg(a.column_name,',') within group(order by COLUMN_POSITION) columns,
                                b.uniqueness
                                from dba_ind_columns a, dba_indexes b
                                where a.table_owner='"""+mts[0].upper()+"""'
                                and a.TABLE_NAME='"""+mts[1].upper()+"""'
                                and a.index_owner=b.owner
                                and a.index_name = b.index_Name
                                group by a.index_Name,b.uniqueness"""
            #权限过滤
            for eqRow in eqResult:
                if eqRow[1]:
                    try:
                        filTab = ora_tables.objects.get(instance_id=self.primaryId,schema_name=eqRow[0].lower(),table=eqRow[1].lower())
                    except Exception as e:
                        print(str(e))
                        finalStatus = '数据字典过旧'
                        msg = '数据字典没有该表'
                        return finalStatus,msg,headerList,queryResult
                    cnt = ora_tab_privs.objects.filter(username=logon_user,table_id = filTab.id).count()
                    if cnt == 0:
                        finalStatus = '权限不足'
                        msg = '权限不足: '+eqRow[0]+'.'+eqRow[1]
                        return finalStatus,msg,headerList,queryResult
            try:
                cr.execute(sqlContent)
            except Exception as e:
                finalStatus = '执行异常'
                msg = str(e)
            else:
                headerList = [row[0] for row in cr.description]
                queryResult = cr.fetchall()
        else:
            finalStatus = '不支持的操作'
            msg = "不支持的操作,该页面仅支持查询操作!"

        return finalStatus,msg,headerList,queryResult
