#archer o版

````
python 3.6
yum install python-devel openldap-devel
````

#语言及环境:
* mysql5.6及以上
* django == 1.8.17
* django-celery==1.3.0
* cx_Oracle
* pymysql
* django-auth-ldap
* ldap
* Crypto
* pycrypto
* paramiko
* sqlparse

#安装model：
````
mysql -uroot
create database autops
python manage.py migrate auth
python manage.py migrate
````
#创建超级用户:
````
python manage.py createsuperuser
````
#启动:
````
export C_FORCE_ROOT=1
python manage.py runserver 0.0.0.0:8080
````
#或使用gunicorn+nginx启动
./startup.sh
#启动celery
````
python manage.py celery worker --loglevel=info --autoreload -B
````
