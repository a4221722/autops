#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import sys
import os

headers = {'Content-Type': 'application/json;charset=utf-8'}
api_url = "https://oapi.dingtalk.com/robot/send?access_token=xxx"

def dingAlert(text,mobile):
    json_text= {
     "msgtype": "text",
        "at": {
            "atMobiles": [
                mobile
            ],
            "isAtAll": False
        },
        "text": {
            "content": text
        }
    }
    print(requests.post(api_url,json.dumps(json_text),headers=headers).content)

if __name__ == '__main__':
    text = sys.argv[1]
    mobile = sys.argv[2]
    dingAlert(text,mobile)

