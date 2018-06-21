import paramiko

class OsInf():
    def __init__(self,address,username,password,port=22):
        self.osclient = paramiko.SSHClient()
        self.osclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.osclient.connect(address, port, username = username, password=password, timeout=4)

    def getLoad(self):
        stdin, stdout, stderr = self.osclient.exec_command('cat /proc/loadavg')
        for res in stdout:
            res=res.rstrip('\n').split(' ')
        return res[0]

