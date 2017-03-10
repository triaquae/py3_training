import socket
import os ,json
import optparse
import getpass
import hashlib
import sys 

STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
}



class FTPClient(object):
    def __init__(self):

        self.user = None


        parser = optparse.OptionParser()
        parser.add_option("-s","--server", dest="server", help="ftp server ip_addr")
        parser.add_option("-P","--port",type="int", dest="port", help="ftp server port")
        parser.add_option("-u","--username", dest="username", help="username")
        parser.add_option("-p","--password", dest="password", help="password")
        self.options , self.args = parser.parse_args()
        self.verify_args(self.options,self.args)
        self.make_connection()

    def make_connection(self):
        self.sock = socket.socket()
        self.sock.connect((self.options.server,self.options.port))

    def verify_args(self, options,args):
        '''校验参数合法型'''

        if options.username is not None and options.password is not None:
            pass
        elif options.username is None and options.password is None:
            pass
        else:
            #options.username is None or options.password is None:
            exit("Err: username and password must be provided together..")

        if options.server and options.port:
            #print(options)
            if options.port >0 and options.port <65535:
                return True
            else:
                exit("Err:host port must in 0-65535")
        else:
            exit("Error:must supply ftp server address, use -h to check all available arguments.")

    def authenticate(self):
        '''用户验证'''
        if self.options.username:
            print(self.options.username,self.options.password)
            return  self.get_auth_result(self.options.username, self.options.password)
        else:
            retry_count = 0
            while retry_count <3:
                username = input("username:").strip()
                password = input("password:").strip()
                if self.get_auth_result(username,password):
                    return True
                retry_count += 1



    def get_auth_result(self,user,password):
        data = {'action':'auth',
                'username':user,
                'password':password}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()

        if response.get('status_code') == 254:
            print("Passed authentication!")
            self.user = user
            return True
        else:
            print(response.get("status_msg"))

    def get_response(self):
        '''得到服务器端回复结果'''
        data = self.sock.recv(1024)
        #print("server res", data)
        data = json.loads(data.decode())
        return data



    def interactive(self):
        if self.authenticate():
            print("---start interactive with u...")
            self.terminal_display = "[%s]$:"%self.user
            while True:
                choice = input(self.terminal_display).strip()
                if len(choice) == 0:continue
                cmd_list = choice.split()
                if hasattr(self,"_%s"%cmd_list[0]):
                    func = getattr(self,"_%s"%cmd_list[0])
                    func(cmd_list)
                else:
                    print("Invalid cmd,type 'help' to check available commands. ")
    
    def __md5_required(self,cmd_list):
        '''检测命令是否需要进行MD5验证'''
        if '--md5' in cmd_list:
            return True


    def _help(self,*args,**kwargs):
        supported_actions = """
        get filename    #get file from FTP server
        put filename    #upload file to FTP server
        ls              #list files in current dir on FTP server
        pwd             #check current path on server
        cd path         #change directory , same usage as linux cd command
        """
        print(supported_actions)

    def show_progress(self,total):
        received_size = 0 
        current_percent = 0 
        while received_size < total:
             if int((received_size / total) * 100 )   > current_percent :
                  print("#",end="",flush=True)
                  current_percent = int((received_size / total) * 100 )
             new_size = yield 
             received_size += new_size

    def _cd(self,*args,**kwargs):
        #print("cd args",args)
        if len(args[0]) >1:
            path = args[0][1]
        else:
            path = ''
        data = {'action': 'change_dir','path':path}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        if response.get("status_code") == 260:
            self.terminal_display ="%s:" % response.get('data').get("current_path")


    def _pwd(self,*args,**kwargs):
        data = {'action':'pwd'}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        has_err = False
        if response.get("status_code") == 200:
            data = response.get("data")

            if data:
                print(data)
            else:
                has_err = True
        else:
            has_err = True

        if has_err:
            print("Error:something wrong.")

    def _ls(self,*args,**kwargs):
        data = {'action':'listdir'}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        has_err = False
        if response.get("status_code") == 200:
            data = response.get("data")

            if data:
                print(data[1])
            else:
                has_err = True
        else:
            has_err = True

        if has_err:
            print("Error:something wrong.")



    def _get(self,cmd_list):
        print("get--",cmd_list)
        if len(cmd_list) == 1:
            print("no filename follows...")
            return
        data_header = {
            'action':'get',
            'filename':cmd_list[1]
        }
        if self.__md5_required(cmd_list):
            data_header['md5'] = True

        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()
        print(response)
        if response["status_code"] == 257:#ready to receive
            self.sock.send(b'1')#send confirmation to server 
            base_filename = cmd_list[1].split('/')[-1]
            received_size = 0
            file_obj = open(base_filename,"wb")
            if response['data']['file_size'] == 0:
                file_obj.close()
                return

            if self.__md5_required(cmd_list):
                md5_obj = hashlib.md5()
                progress = self.show_progress(response['data']['file_size']) #generator
                progress.__next__()
                while received_size < response['data']['file_size']:
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    try:
                      progress.send(len(data))
                    except StopIteration as e:
                      print("100%")
                    file_obj.write(data)
                    md5_obj.update(data)
                else:
                    print("----->file recv done----")
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    md5_from_server = self.get_response()
                    if md5_from_server['status_code'] == 258:
                        if md5_from_server['md5'] == md5_val:
                            print("%s 文件一致性校验成功!" % base_filename)
                    #print(md5_val,md5_from_server)

            else:
                progress = self.show_progress(response['data']['file_size']) #generator
                progress.__next__()

                while received_size < response['data']['file_size']:
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    file_obj.write(data)
                    try:
                      progress.send(len(data))
                    except StopIteration as e:
                      print("100%")

                else:
                    print("----->file rece done----")
                    file_obj.close()

if __name__ == "__main__":
    ftp = FTPClient()
    ftp.interactive() #交互
