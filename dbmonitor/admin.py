# -*- coding: UTF-8 -*- 
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

# Register your models here.
from .models import os_host_config



class os_host_configAdmin(admin.ModelAdmin):
    list_display = ('id', 'host_name','host_ip','host_port','host_user','create_time', 'update_time')
    search_fields = ['id', 'host_name','host_ip','host_port','host_user','create_time', 'update_time']

admin.site.register(os_host_config, os_host_configAdmin)
