# -*- coding: utf-8 -*-

from os.path import isfile
from resources.lib.settings import getTablesStructure, getAddonIcon, getEpgDbFilePath
from xbmc import executebuiltin, log, LOGERROR
from sqlite3 import connect as SqliteConnect, Error as SqliteError
from resources.lib.strings import DIALOG_TITLE, DB_CONNECTION_ERROR, DB_CREATE_TABLES_ERROR
from datetime import datetime as dt
from time import strptime as time_strptime

'''
Display a basic notification
'''    

def notify(message, plus=None):
    message = message.encode("utf-8", 'ignore')
    log(message, LOGERROR)
    if not plus is None:
        log(plus, LOGERROR)
        
    executebuiltin('Notification(%s,%s,%s,%s)'%(DIALOG_TITLE.encode("utf-8", 'ignore'), message, 6000, getAddonIcon()))
    
    
    
'''
Return a datetim from string as %Y%m%d%H%M%S
'''
def strToDatetime(datestr):
    try:
        return dt.strptime(datestr, "%Y%m%d%H%M%S")
    except TypeError:
        return dt(*(time_strptime(datestr, "%Y%m%d%H%M%S")[0:6]))
    
    
    
'''
Database connection.
    '''
def connectEpgDB():
    
    def connect():
        try:
            database = SqliteConnect(getEpgDbFilePath())
            database.text_factory = str
            cursor = database.cursor()
        except SqliteError as e:
            notify(DB_CONNECTION_ERROR, e.message)
            return None
        
        return database, cursor
    
    
    if not isfile(getEpgDbFilePath()):
        database, cursor = connect()
        if database is None:
            return None, None
        
        channels_str, programs_str, updates = getTablesStructure()      
        update_flag  = "INSERT INTO updates (time) VALUES ('-1')"
        
        try:
            cursor.execute(channels_str)
            cursor.execute(programs_str)
            cursor.execute(updates)
            cursor.execute(update_flag)
            database.commit()
            
        except SqliteError as e:
            notify(DB_CREATE_TABLES_ERROR, e.message)
            return None, None
        return database, cursor

    else:
        return connect()
    
    

'''
Copy a file from source to dest.
'''
def copyfile(source, dest, buffer_size=1024*1024):
    
    source = open(source, "rb")
    destin = open(dest, "wb")
    
    while 1:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        destin.write(copy_buffer)