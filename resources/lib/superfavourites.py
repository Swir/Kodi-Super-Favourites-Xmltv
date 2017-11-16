# -*- coding: utf-8 -*-
import os
import xbmc
import sqlite3
from resources.lib import EPGXML, utils
from xbmcgui import DialogProgress


'''
Handle Super favourites iptv subfolders.
'''
class SuperFavouritesIptvFolder(object):
    
    DEBUG = False
    
    addon     = None
    iptv_path = None
    pattern   = None
    
    epg_db   = None 
    database = None
    cursor   = None
    
    SF_XMLTV_ID_PATTERN    = 0
    SF_DISPLAY_NAME_PATERN = 1
    
    
    '''
    Init
    '''
    def __init__(self, addon, debug=False):
        self.DEBUG = debug
        
        self.addon = addon
        self.iptv_path = self.addon.getSetting('super.favourites.folder')
        self.epg_db = EPGXML.EpgDb(self.addon, True)
        self.database, self.cursor = utils.connectEpgDB(self.epg_db, self.addon)
        self.epg_db.setDatabaseObj(self.database)
        self.epg_db.setCursorObj(self.cursor)
        
        try:
            self.pattern = int(self.addon.getSetting('super.favourites.subfolders.pattern'))
        except ValueError:
            self.pattern = SuperFavouritesIptvFolder.SF_XMLTV_ID_PATTERN
    
    
    '''
    Create the base subfolders structure.
    '''
    def createSubFolders(self):
        progress = DialogProgress()
        try:
            progress.create(self.addon.getLocalizedString(322245), self.addon.getLocalizedString(322246))
            row = "id_channel" if self.pattern == SuperFavouritesIptvFolder.SF_XMLTV_ID_PATTERN else 'display_name' 
            request = "SELECT %s FROM channels" % row
            
            if self.database is None or self.cursor is None:
                utils.notify(self.addon, 322244)
                progress.close()
                return
            
            self.cursor.execute(request)
            channels = self.cursor.fetchall()
            
            i = 1
            for channel in channels:
                percent = int( ( i / float(len(channels)) ) * 100)
                
                if not os.path.isfile(xbmc.translatePath(os.path.join(self.iptv_path, channel[0]))):
                    try:
                        os.mkdir(os.path.join(xbmc.translatePath(self.iptv_path), channel[0]))
                    except OSError:
                        pass
                
                message = self.addon.getLocalizedString(322247) + ' %i/%i' % (i, len(channels))
                progress.update(percent, "", message)
                i += 1
                
        except sqlite3.Error:
            progress.close()
            if self.DEBUG:
                utils.notify(self.addon, 322244)
        progress.close()   
        
        
    
    
    '''
    Return the subfolder of given iptv channel.
    '''
    def getSubFolder(self, id_channel):
        pass
    
    
    '''
    Cose the database oject
    '''
    def close(self):
        try:
            self.database.close()
            del self.cursor
            del self.database
        except:
            pass