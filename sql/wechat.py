#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests,sys,json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Corpid = "ww490aca0759b3b53f"                                                   # CorpID是企业号的标识
Secret = "i2pS69cwYTSssqgqkNtN8ptVBHuX670O3mS4aNlTRFk"                          # Secret是管理组凭证密钥
#Tagid = "1"                                                                    # 通讯录标签ID
Agentid = "1000002"

class WechatAlert():

    def getToken(self,Corpid,Secret):
        Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        Data = {
            "corpid":Corpid,
            "corpsecret":Secret
        }
        r = requests.get(url=Url,params=Data,verify=False)
        Token = r.json()['access_token']
        return Token


    def sendMessage(self,User,Subject,Content):
        Token = self.getToken(Corpid,Secret)
        Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
        Data = {
            "touser": User,                                 # 企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送。
            "msgtype": "text",                              # 消息类型。
            "agentid": Agentid,                             # 企业号中的应用id。
            "text": {
                "content": Subject + '\n' + Content
            },
            "safe": "0"
        }
        r = requests.post(url=Url,data=json.dumps(Data),verify=False)
        return r.text


if __name__ == '__main__':
    User = sys.argv[1]                                                              # zabbix传过来的第一个参数
    Subject = sys.argv[2]                                                           # zabbix传过来的第二个参数
    Content = sys.argv[3]                                                           # zabbix传过来的第三个参数

    wechatalert = WechatAlert()
    Status = wechatalert.sendMessage(User,Subject,Content)
    print(Status)

