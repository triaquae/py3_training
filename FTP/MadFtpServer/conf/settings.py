
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


USER_HOME = "%s/home" % BASE_DIR
LOG_DIR =  "%s/log" % BASE_DIR
LOG_LEVEL = "DEBUG"

ACCOUNT_FILE = "%s/conf/accounts.cfg" % BASE_DIR


HOST = "0.0.0.0"
PORT = 9999


