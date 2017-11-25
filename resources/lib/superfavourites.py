# -*- coding: utf-8 -*-
from os import mkdir
from os.path import isfile, join
from xbmcgui import DialogProgress
from sqlite3 import Error as SqliteError

from resources.lib.strings import SF_DIR_STRING, SF_CHANNELS_INFOS_ERROR
from resources.lib.strings import SF_SUBFOLDERS_PROGRESS_HEADER, SF_SUBFOLDERS_PROGRESS_MSG
from resources.lib.utils import notify, connectEpgDB
from resources.lib.EPGXML import EpgDb
from resources.lib.settings import DEBUG, getSFFolder, getSFFoldersPattern, AddonConst

'''
Handle Super favourites iptv subfolders.
'''
class SuperFavouritesIptvFolder(object):
            
    epg_db = database = cursor = None 
    
    '''
    Init
    '''
    def __init__(self):
        
        self.epg_db = EpgDb()
        self.database, self.cursor = connectEpgDB()
        self.epg_db.setDatabaseObj(self.database)
        self.epg_db.setCursorObj(self.cursor)
    
    
    '''
    Create the base subfolders structure.
    '''
    def createSubFolders(self):
        progress = DialogProgress()
        try:
            progress.create(SF_SUBFOLDERS_PROGRESS_HEADER, SF_SUBFOLDERS_PROGRESS_MSG)
            row = "id_channel" if getSFFoldersPattern() == AddonConst.SF_XMLTV_ID_PATTERN else 'display_name' 
            request = "SELECT %s FROM channels" % row
            
            if self.database is None or self.cursor is None:
                notify(SF_CHANNELS_INFOS_ERROR)
                progress.close()
                return
            
            self.cursor.execute(request)
            channels = self.cursor.fetchall()
            
            i = 1
            for channel in channels:
                
                if not isfile(join(getSFFolder(translate=True), channel[0])):
                    try:
                        mkdir(join(getSFFolder(translate=True), channel[0]))
                    except OSError:
                        pass
                    
                progress.update(int( ( i / float(len(channels)) ) * 100), "", 
                                SF_DIR_STRING + ' %i/%i' % (i, len(channels)))
                i += 1
                
        except SqliteError:
            progress.close()
            if DEBUG:
                notify(SF_CHANNELS_INFOS_ERROR)
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