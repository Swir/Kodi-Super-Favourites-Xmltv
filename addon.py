# -*- coding: utf-8 -*-
import xbmc, xbmcgui  

from resources.lib import EPGXML, superfavourites
from resources.lib.EPGCtl import EPGGridView
from resources.lib import strings, settings
from resources.lib.utils import connectEpgDB

'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    
    epgDb = epgXml = epgView = None
        
    '''
    Class init.
    '''    
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        
    
    '''
    Gui values init.
    '''
    def onInit(self):
        database, cursor = connectEpgDB()
        
        self.epgView = EPGGridView(self)
        self.epgDb   = EPGXML.EpgDb(database, cursor)
        self.epgView.setGlobalDataGrid(self.epgDb.getEpgGrid())  
        
        self.epgView.displayChannels()
        self.epgView.setFocus(0, 0)
            
    '''
    Handle all xbmc action messages.
    '''
    def onAction(self, action):

        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
            self.epgView.is_closing = True
            self.epgDb.close()
            del self.epgView
            self.close()
        
        # Grid actions    
        elif action == xbmcgui.ACTION_MOVE_LEFT :
            self.epgView.previous()
                                 
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            self.epgView.next()
        
        elif action in [xbmcgui.ACTION_MOVE_UP, xbmcgui.ACTION_MOUSE_WHEEL_UP]:
                self.epgView.up()
                     
        elif action in [xbmcgui.ACTION_MOVE_DOWN, xbmcgui.ACTION_MOUSE_WHEEL_DOWN]:
            self.epgView.down()
                    
        

    '''
    Handle all controls clicks, provide a control ID
    '''
    def onClick(self, controlID):
        pass
        
       
    '''
    Handle focusses changes between controls
    '''
    def onFocus(self, controlID):
         
        if self.epgView.isProgramControl(controlID):
            self.epgView.setInfos(controlID) 
        
        

''''''''''''''''''''''''''''''
'''    Plugin entry point. '''
''''''''''''''''''''''''''''''

if __name__ == '__main__':    
    # Checking for bad configuration.   
    ok, error_msg = settings.checkMandatorySettings()
    if not ok:
        xbmcgui.Dialog().ok(strings.DIALOG_TITLE, strings.BAD_ADDON_CONFIGURATION, 
                            error_msg, strings.CONFIGURATION_TAKE_TIME_MSG)
        settings.addon.openSettings()
    
    else:      
        database, cursor = connectEpgDB()
        epgDb = EPGXML.EpgDb(database, cursor) 
        # Populate and create tables in case of first start
        if epgDb.firstTimeRuning():
            xbmcgui.Dialog().ok(strings.DIALOG_TITLE, strings.SFX_FIRST_START_DETECTED)
            epgXml = EPGXML.EpgXml(database, cursor, progress_bar=True)
            
            if epgXml.getXMLTV():
                epgDb.setFirstTimeRuning(0)
                epgDb.setUpdateDate()
                xbmc.sleep(1000)
                # Super favourites folder init.
                sf_folder = superfavourites.SuperFavouritesIptvFolder()
                sf_folder.createSubFolders()
                # All is done, restart required
                xbmcgui.Dialog().ok(strings.DIALOG_TITLE, strings.SFX_INIT_OK)
                sf_folder.close()
            
            epgDb.close()
            epgXml.close()
            del epgDb
            del epgXml
                   
        # Else, update epg in a thread
        else:
            # Starting GUI
            EPGgui = XMLWindowEPG('epg.xml', settings.getAddonPath())
            EPGgui.doModal() 
            del EPGgui        
        