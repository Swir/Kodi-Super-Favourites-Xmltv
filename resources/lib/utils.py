# -*- coding: utf-8 -*-

import xbmc
import sqlite3
from os.path import isfile

'''
Display a basic notification
'''    

def notify(addon, message, plus=None):
    
    n_time  = '10000'
    n_title = 'Super Favourites XMLTV'
    n_logo  = addon.getAddonInfo('icon')
    message = addon.getLocalizedString(message).encode("utf-8")
    
    xbmc.log(message, xbmc.LOGERROR)
    if not plus is None:
        xbmc.log(plus, xbmc.LOGERROR)
        
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)'%(n_title, message, n_time, n_logo))
    
    
'''
Database connection.
    '''
def connectEpgDB(epg_db_obj, addon):
    
    def connect(epg_db_obj, addon):
        try:
            database = sqlite3.connect(epg_db_obj.db_path)
            database.text_factory = str
            cursor = database.cursor()
        except sqlite3.Error as e:
            notify(addon, 33401, e.message)
            return None
        
        return database, cursor
    
    
    if not isfile(epg_db_obj.db_path):
        database, cursor = connect(epg_db_obj, addon)
        if database is None:
            return None, None
        
        channels_str = "CREATE TABLE channels (id INTEGER PRIMARY KEY AUTOINCREMENT, id_channel TEXT, display_name TEXT, logo TEXT, source TEXT, visible BOOLEAN)"
        programs_str = "CREATE TABLE programs (id_program INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, start_date TEXT, end_date TEXT, description TEXT)"
        updates      = "CREATE TABLE updates (id_update INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP)"        
        
        update_flag  = "INSERT INTO updates (time) VALUES ('-1')"
        try:
            cursor.execute(channels_str)
            cursor.execute(programs_str)
            cursor.execute(updates)
            cursor.execute(update_flag)
            database.commit()
            
        except sqlite3.Error as e:
            notify(addon, 33402, e.message)
            return None, None
        return database, cursor

    else:
        return connect(epg_db_obj, addon)
    
    

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