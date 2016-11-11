#!_*_coding:utf-8_*_
#__author__:"Alex Li"

'''
handle all the database interactions
'''
import json,time ,os
from  conf import settings
def file_db_handle(conn_params):
    '''
    parse the db file path
    :param conn_params: the db connection params set in settings
    :return:
    '''
    print('file db:',conn_params)
    #db_path ='%s/%s' %(conn_params['path'],conn_params['name'])
    return file_execute

def db_handler():
    '''
    connect to db
    :param conn_parms: the db connection params set in settings
    :return:a
    '''
    conn_params = settings.DATABASE
    if conn_params['engine'] == 'file_storage':
        return file_db_handle(conn_params)
    elif conn_params['engine'] == 'mysql':
        pass #todo



def file_execute(sql,**kwargs):
    conn_params = settings.DATABASE
    db_path = '%s/%s' % (conn_params['path'], conn_params['name'])

    print(sql,db_path)
    sql_list = sql.split("where")
    print(sql_list)
    if sql_list[0].startswith("select") and len(sql_list)> 1:#has where clause
        column,val = sql_list[1].strip().split("=")

        if column == 'account':
            account_file = "%s/%s.json" % (db_path, val)
            print(account_file)
            if os.path.isfile(account_file):
                with open(account_file, 'r') as f:
                    account_data = json.load(f)
                    return account_data
            else:
                exit("\033[31;1mAccount [%s] does not exist!\033[0m" % val )

    elif sql_list[0].startswith("update") and len(sql_list)> 1:#has where clause
        column, val = sql_list[1].strip().split("=")
        if column == 'account':
            account_file = "%s/%s.json" % (db_path, val)
            #print(account_file)
            if os.path.isfile(account_file):
                account_data = kwargs.get("account_data")
                with open(account_file, 'w') as f:
                    acc_data = json.dump(account_data, f)
                return True