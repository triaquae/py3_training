#!_*_coding:utf-8_*_
#__author__:"Alex Li"

import json
import time
from core import db_handler
from conf import settings


def load_current_balance(account_id):
    '''
    return account balance and other basic info
    :param account_id:
    :return:
    '''
    # db_path = db_handler.db_handler(settings.DATABASE)
    # account_file = "%s/%s.json" %(db_path,account_id)
    #
    db_api = db_handler.db_handler()
    data = db_api("select * from accounts where account=%s" % account_id)

    return data

    # with open(account_file) as f:
    #     acc_data = json.load(f)
    #     return  acc_data
def dump_account(account_data):
    '''
    after updated transaction or account data , dump it back to file db
    :param account_data:
    :return:
    '''
    db_api = db_handler.db_handler()
    data = db_api("update accounts where account=%s" % account_data['id'],account_data=account_data)

    # db_path = db_handler.db_handler(settings.DATABASE)
    # account_file = "%s/%s.json" %(db_path,account_data['id'])
    # with open(account_file, 'w') as f:
    #     acc_data = json.dump(account_data,f)

    return True