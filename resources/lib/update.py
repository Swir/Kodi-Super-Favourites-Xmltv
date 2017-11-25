# -*- coding: utf-8 -*-
from threading import Thread
from datetime import datetime as dt
from time import time
from xbmc import sleep as kodisleep, log, LOGERROR

from resources.lib.EPGXML import EpgDb, EpgXml
from resources.lib.strings import DEBUG_HEADER 
from resources.lib.utils import connectEpgDB, strToDatetime
from resources.lib.settings import doStartupUpdate, getUpdateFrequency

'''
Handle threaded updates
''' 
class ThreadedUpdater(Thread):
    
    '''
    Thread init
    '''
    def __init__(self):
        Thread.__init__(self)
    
    
    '''
    Thread run
    '''
    def run(self):
        try:
            epg_db = EpgDb()
            kodisleep(40000)
            
            database, cursor = connectEpgDB()   
            epg_db.setDatabaseObj(database)
            epg_db.setCursorObj(cursor)
            # Getting last update date.
            update_date = epg_db.getLastUpdateDate()
            
            if not doStartupUpdate() or epg_db.firstTimeRuning():
                return   
                                    
            current_time = dt.fromtimestamp(time())
            update_time = strToDatetime(update_date)
                    
            delta = current_time - update_time
                        
            if delta.days < getUpdateFrequency() :        
                return
            
            epg_xml = EpgXml(progress_bar=False)
            epg_xml.setDatabaseObj(database)
            epg_xml.setCursorObj(cursor)
            epg_xml.getXMLTV()
            epg_db.setUpdateDate()
                
            epg_xml.close() 
            epg_db.close()
            del epg_xml
            del epg_db
            
        except Exception as e:
            log("%s %s" % ( DEBUG_HEADER, e.message), LOGERROR)
            