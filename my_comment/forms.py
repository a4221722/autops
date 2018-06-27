from django import forms
from django_comments.forms import CommentForm
from my_comment.models import MyComment

class MyCommentForm(CommentForm):
    def get_comment_list(self):
        data = super(CommentFormWithTitle, self).get_comment_create_data().sort(key= lambda x:x['submit_date'])
        return data
