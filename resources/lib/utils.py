# -*- coding: utf-8 -*-

import xbmc
import sqlite3
from os.path import isfile
from resources.lib import settings, strings

'''
Display a basic notification
'''    

def notify(message, plus=None):
    
    xbmc.log(message, xbmc.LOGERROR)
    if not plus is None:
        xbmc.log(plus, xbmc.LOGERROR)
        
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)'%(strings.DIALOG_TITLE, message, 6000, settings.getAddonIcon()))
    
    
'''
Database connection.
    '''
def connectEpgDB():
    
    def connect():
        try:
            database = sqlite3.connect(settings.getEpgDbFilePath())
            database.text_factory = str
            cursor = database.cursor()
        except sqlite3.Error as e:
            notify(strings.DB_CONNECTION_ERROR, e.message)
            return None
        
        return database, cursor
    
    
    if not isfile(settings.getEpgDbFilePath()):
        database, cursor = connect()
        if database is None:
            return None, None
        
        channels_str, programs_str, updates = settings.getTablesStructure()      
        update_flag  = "INSERT INTO updates (time) VALUES ('-1')"
        
        try:
            cursor.execute(channels_str)
            cursor.execute(programs_str)
            cursor.execute(updates)
            cursor.execute(update_flag)
            database.commit()
            
        except sqlite3.Error as e:
            notify(strings.DB_CREATE_TABLES_ERROR, e.message)
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