# -*- coding: utf-8 -*-
import os
import xbmc
from resources.lib import EPGXML, utils



'''
Handle Super favourites iptv subfolders.
'''
class SuperFavouritesIptvFolder(object):
    
    addon = None
    iptv_path = None
    
    epg_db, database, cursor = None
    
    '''
    Init
    '''
    def __init__(self, addon):
        self.addon = addon
        self.iptv_path = self.addon.getSetting('super.favourites.folder')
        self.epg_db = EPGXML.EpgDb(addon, True)
        self.database, self.cursor = utils.connectEpgDB(self.epg_db, self.addon)
        self.epg_db.setDatabaseObj(self.database)
        self.epg_db.setCursorObj(self.cursor)
    
    
    '''
    Create the base subfolders structure.
    '''
    def createSubFolders(self):
        pass
    
    
    
    '''
    Return the subfolder of given iptv channel.
    '''
    def getSubFolder(self, id_channel):
        pass
    