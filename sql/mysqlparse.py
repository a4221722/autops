import sqlparse

class MySqlparse():
    def __init__(self,*args,**kwargs):
        if sqlparse.keywords.KEYWORDS.get('DO'):
            sqlparse.keywords.KEYWORDS.pop('DO')

    def parse(self,*args,**kwargs):
        return sqlparse.parse(*args,**kwargs)

    def split(self,*args,**kwargs):
        return sqlparse.split(*args,**kwargs)
