import time

def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
