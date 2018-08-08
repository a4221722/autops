# -*- coding: UTF-8 -*- 
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

# Register your models here.
from .models import users,  workflow, ora_primary_config, ora_tab_privs



class ora_primary_configAdmin(admin.ModelAdmin):
    list_display = ('id', 'cluster_name','primary_host','primary_port','primary_srv','primary_user','standby_host','standby_port','standby_srv','create_time', 'dict_time')
    search_fields = ['id', 'cluster_name','primary_host','primary_port','primary_srv','primary_user','standby_host','standby_port','standby_srv','create_time', 'dict_time']

class workflowAdmin(admin.ModelAdmin):
    list_per_page=5
    list_display = ('id','workflow_name', 'engineer', 'review_man', 'create_time', 'finish_time', 'status',   'cluster_name', 'reviewok_time', 'sql_content',)
    search_fields = ['id','workflow_name', 'engineer', 'review_man', 'sql_content']

#创建用户表单重新定义，继承自UserCreationForm
class usersCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(usersCreationForm, self).__init__(*args, **kwargs)
        self.fields['role'].required = True

#编辑用户表单重新定义，继承自UserChangeForm
class usersChangeForm(UserChangeForm): 
    def __init__(self, *args, **kwargs):
        super(usersChangeForm, self).__init__(*args, **kwargs)
        self.fields['role'].required = True
        self.fields['wechat_account'].required = False
        self.fields['display'].required = False
        self.fields['mobile'].required = False

class usersAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(usersAdmin, self).__init__(*args, **kwargs)
        self.list_display = ('id', 'username', 'display', 'role', 'email','wechat_account','mobile', 'password', 'is_superuser', 'is_active')
        self.search_fields = ('id', 'username', 'display', 'role', 'email')
        self.form = usersChangeForm
        self.add_form = usersCreationForm
        #以上的属性都可以在django源码的UserAdmin类中找到，我们做以覆盖

    def changelist_view(self, request, extra_context=None):  
        #这个方法在源码的admin/options.py文件的ModelAdmin这个类中定义，我们要重新定义它，以达到不同权限的用户，返回的表单内容不同
        if request.user.is_superuser:
            #此字段定义UserChangeForm表单中的具体显示内容，并可以分类显示
            self.fieldsets = (
                              (('认证信息'), {'fields': ('username', 'password')}),
                              (('个人信息'), {'fields': ('display', 'role', 'email','wechat_account','mobile')}),
                              (('权限信息'), {'fields': ('is_active', 'is_staff')}),
                              #(('Important dates'), {'fields': ('last_login', 'date_joined')}),
                              )
            #此字段定义UserCreationForm表单中的具体显示内容
            self.add_fieldsets = ((None, {'classes': ('wide',),
                                          'fields': ('username', 'display', 'role', 'email','wechat_account','mobile', 'password1', 'password2'),
                                          }),
                                  )
        return super(usersAdmin, self).changelist_view(request, extra_context)

admin.site.register(users, usersAdmin)
admin.site.register(ora_primary_config,ora_primary_configAdmin)
admin.site.register(workflow, workflowAdmin)
