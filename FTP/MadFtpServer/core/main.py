
import optparse
from core.ftp_server import FTPHandler
import socketserver
from conf import settings


class ArvgHandler(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        # parser.add_option("-s","--host",dest="host",help="server binding host address")
        # parser.add_option("-p","--port",dest="port",help="server binding port")
        (options, args) = self.parser.parse_args()

        self.verify_args(options, args)

    def verify_args(self,options,args):
        '''校验并调用相应的功能'''
        if args:
            if hasattr(self,args[0]):
                func = getattr(self,args[0])
                func()
            else:
                exit("usage:start/stop")

        else:
            exit("usage:start/stop")

    def start(self):
        print('---\033[32;1mStarting FTP server on %s:%s\033[0m----' %(settings.HOST, settings.PORT))
        # Create the server, binding to localhost on port 9999
        server = socketserver.ThreadingTCPServer((settings.HOST, settings.PORT), FTPHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()




