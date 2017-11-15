# -*- coding: utf-8 -*-

import xbmc
import EPGXML
import sqlite3
import time, datetime
from os.path import isfile

'''
Display a basic notification
    '''    
from threading import Thread


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
        
        channels_str = "CREATE TABLE channels (id TEXT, display_name TEXT, logo TEXT, source TEXT, visible BOOLEAN, PRIMARY KEY (id))"
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
        


'''
Handle threaded updates
''' 
class ThreadedUpdater(Thread):
    
    epg_db = None
    epg_xml = None
    addon = None
    
    database = None
    cursor = None
    
    
    '''
    Thread init
    '''
    def __init__(self, addon):
        Thread.__init__(self)
        self.addon = addon
        self.epg_db = EPGXML.EpgDb(addon, True)
    
    
    '''
    Thread run
    '''
    def run(self):
        # Removes old entries into the database.
        self.database, self.cursor = connectEpgDB(self.epg_db, self.addon)   
        self.epg_db.setDatabaseObj(self.database)
        self.epg_db.setCursorObj(self.cursor)
        
        # Clean old entries ( see configuration )
        if self.epg_db.firstTimeRuning():
            return
        
        self.epg_db.getCleanOld()
        
        
        
        # Getting EPG xmltv file
        update = False
        treshold = self.addon.getSetting('update.frequency')
        update_date = self.epg_db.getLastUpdateDate()
        
        if not update_date is None:
            if treshold is None or treshold == '':
                treshold = '1'
                    
            current_time = datetime.datetime.fromtimestamp(time.time())
            try:
                update_time = datetime.datetime.strptime(update_date, "%Y%m%d%H%M%S")
            except TypeError:
                update_time = datetime.datetime(*(time.strptime(update_date, "%Y%m%d%H%M%S")[0:6]))
            delta = current_time - update_time
                    
            if delta.days >= int(treshold) + 1 :        
                update = True
        
        
        if update or update_date is None:
            self.epg_xml = EPGXML.EpgXml(self.addon, True, progress_bar=False)
            self.epg_xml.setDatabaseObj(self.database)
            self.epg_xml.setCursorObj(self.cursor)
            self.epg_xml.getXMLTV()
            self.epg_db.setUpdateDate()
            
            self.epg_xml.close()
            del self.epg_xml
            
        self.epg_db.close()
        del self.epg_db
       
    