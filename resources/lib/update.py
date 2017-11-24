# -*- coding: utf-8 -*-

import time, datetime
import xbmc
import utils
from resources.lib import EPGXML, settings, strings
from threading import Thread


'''
Handle threaded updates
''' 
class ThreadedUpdater(Thread):
    
    epg_db = None
    epg_xml = None
    
    database = None
    cursor = None
    
    
    '''
    Thread init
    '''
    def __init__(self):
        Thread.__init__(self)
        self.epg_db = EPGXML.EpgDb(settings.addon, True)
    
    
    '''
    Thread run
    '''
    def run(self):
        try:
            xbmc.sleep(10000)
            # Removes old entries into the database.
            self.database, self.cursor = utils.connectEpgDB()   
            self.epg_db.setDatabaseObj(self.database)
            self.epg_db.setCursorObj(self.cursor)
            
            # Clean old entries ( see configuration )
            if self.epg_db.firstTimeRuning():
                return
            
            self.epg_db.getCleanOld()    
            
            if settings.addon.getSetting('startup.update') == 'true':
                # Getting EPG xmltv file
                update = False
                treshold = settings.addon.getSetting('update.frequency')
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
                    self.epg_xml = EPGXML.EpgXml(settings.addon, True, progress_bar=False)
                    self.epg_xml.setDatabaseObj(self.database)
                    self.epg_xml.setCursorObj(self.cursor)
                    self.epg_xml.getXMLTV()
                    self.epg_db.setUpdateDate()
                
                    self.epg_xml.close()
                    del self.epg_xml
                
            self.epg_db.close()
            del self.epg_db
        except Exception as e:
            xbmc.log("%s %s" % ( strings.DEBUG_HEADER, e.message, xbmc.LOGERROR))
            