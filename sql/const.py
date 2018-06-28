# -*- coding: UTF-8 -*- 

class Const(object):
    workflowStatus = {
                        'autoreviewing': '自动审核中',
                        'manreviewing': '等待审核人审核',
                        'autoreviewwrong': '自动审核不通过',
                        'executing': '执行中',
                        'manexec': '等待手工执行',
                        'abort': '人工终止流程',
                        'finish': '自动执行结束', 
                        'exception': '执行有异常',
                        'manfinish': '手工执行成功',
                        'manexcept': '手工执行异常',
                     }
