# -*- coding: utf-8 -*-
from os import mkdir
from os.path import isfile, join
from xbmcgui import DialogProgress, ControlButton
from sqlite3 import Error as SqliteError

from resources.lib.strings import SF_DIR_STRING, SF_CHANNELS_INFOS_ERROR
from resources.lib.strings import SF_SUBFOLDERS_PROGRESS_HEADER, SF_SUBFOLDERS_PROGRESS_MSG
from resources.lib.strings import VIEW_CHANNEL, NOTIFY_PROGRAM, CHANNEL_ACTIONS
from resources.lib.utils import notify, connectEpgDB
from resources.lib.EPGXML import EpgDb
from resources.lib.settings import DEBUG, getSFFolder, getSFFoldersPattern, AddonConst
from resources.lib.EPGCtl import EPGControl


'''
Handle Super favourites iptv subfolders.
'''
class SuperFavouritesIptvFolder(object):
            
    epg_db = database = cursor = None 
    
    '''
    Init
    '''
    def __init__(self):
        self.database, self.cursor = connectEpgDB()
        self.epg_db = EpgDb(self.database, self.cursor)
    
    
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
        
        
        
class ChannelControler(object):
    
    channel_id = display_name = None
    current = 0
    
    
    def __init__(self, window, focus, nofocus):
        self.window = window        
        self.label = self.window.getControl(EPGControl.label.CHANNEL_DETAIL)
        
        # Channel related actions
        self.actions = ControlButton(985, 655, 250, 40, 
                                     label=CHANNEL_ACTIONS, 
                                     focusTexture=focus, 
                                     noFocusTexture=nofocus, 
                                     textOffsetX= 33, 
                                     textOffsetY=33, 
                                     font="font13", 
                                     textColor="FFFFFFFF", 
                                     shadowColor="80FFFFFF", 
                                     focusedColor="FFFFFFFF"
                                     )
        
        
        self.notif = ControlButton(985, 605, 250, 40, 
                                   label=NOTIFY_PROGRAM, 
                                   focusTexture=focus, 
                                   noFocusTexture=nofocus, 
                                   textOffsetX=33, 
                                   textOffsetY=33,
                                   font="font13", 
                                   textColor="FFFFFFFF", 
                                   shadowColor="80FFFFFF", 
                                   focusedColor="FFFFFFFF"
                                   )
        
        # Channel related actions
        self.sf_links = ControlButton(985, 557, 250, 40, 
                                     label=VIEW_CHANNEL, 
                                     focusTexture=focus, 
                                     noFocusTexture=nofocus, 
                                     textOffsetX=33, 
                                     textOffsetY=33, 
                                     font="font13", 
                                     textColor="FFFFFFFF", 
                                     shadowColor="80FFFFFF", 
                                     focusedColor="FFFFFFFF"
                                     )
        
        
        self.window.addControl(self.actions)
        self.window.addControl(self.notif)
        self.window.addControl(self.sf_links)
        self.current = self.sf_links
    
    
    
    '''
    Set the channel id
    '''
    def setChannel(self, channel_id, display_name):   
        self.channel_id = channel_id
        self.display_name = display_name
        self.label.setLabel(display_name)
        
    
    
    '''
    Set focus on actions grid.
    '''
    def setFocus(self):
        self.window.setFocus(self.current)
    
    
    '''
    Go to the next button
    '''
    def next(self):
        if self.current == self.sf_links:
            self.current = self.notif
        elif self.current == self.notif:
            self.current = self.actions
        elif self.current == self.actions:
            self.current = self.sf_links
        self.setFocus()
    
    
    '''
    Go to the previous button
    '''
    def previous(self):
        if self.current == self.sf_links:
            self.current = self.actions
        elif self.current == self.notif:
            self.current = self.sf_links
        elif self.current == self.actions:
            self.current = self.notif
        self.setFocus()
    
    
    '''
    Reset the current control state.
    '''
    def reset(self):
        pass
       
    
    '''
    Return controls IDs
    '''
    def getControls(self):
        return [self.actions.getId(), self.notif.getId(), self.sf_links.getId()]
    
    