from django.db import models
from django_comments.abstracts import CommentAbstractModel
from sql.tasks import wechatDba
from sql.models import workflow,users
import json
# Create your models here.
class MyComment(CommentAbstractModel):

    class Meta:
        ordering = ['-submit_date']

    def save(self,*args,**kwargs):
        if self.is_public:
            workflowObj = workflow.objects.get(id=self.object_pk)
            strTitle = '工单新评论提醒 # '+self.object_pk
            reviewMen = json.loads(workflowObj.review_man)
            commentUser = users.objects.get(username = self.user_name)
            strContent = '评论人：'+commentUser.username+'\n工单名称: '+workflowObj.workflow_name+'\n评论内容: '+self.comment
            for reviewMan in reviewMen:
                if commentUser.username != reviewMan:
                    reviewManObj = users.objects.get(username = reviewMan)
                    wechatDba.delay(strTitle,strContent,reviewManObj.wechat_account)
        super(MyComment,self).save(*args, **kwargs)
