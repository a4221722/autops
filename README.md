#archer o版

yum install python-devel openldap-devel

#语言及环境:
* mysql5.6及以上
* django == 1.8.17
* django-celery
* cx_Oracle
* pymysql
* django-auth-ldap
* ldap
* Crypto
* pycrypto

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
python manager.py 0.0.0.0:8080
python manage.py celery worker --loglevel=info
````
