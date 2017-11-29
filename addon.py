# -*- coding: utf-8 -*-
import datetime
import datetime as dt
import xbmc, xbmcgui  

from threading import Timer
from xbmcgui import ACTION_MOVE_DOWN, ACTION_MOUSE_WHEEL_DOWN, ACTION_MOVE_UP, \
                    ACTION_MOUSE_WHEEL_UP, ACTION_MOVE_RIGHT, ACTION_MOVE_LEFT

from resources.lib import EPGXML, superfavourites
from resources.lib.EPGCtl import EPGControl, EPGGridView
from resources.lib import strings, settings
from resources.lib.utils import connectEpgDB

'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    
    epgDb = epgXml = epgView = None
    is_closing = False
        
    '''
    Class init.
    '''    
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        
    
    '''
    @overrided
    Gui values init.
    '''
    def onInit(self):
        
        # Init EPG Grid global View
        globalControl = self.getControl(EPGControl.GLOBAL_CONTROL)
        
        self.epgView = EPGGridView(self)

        self.epgView.left, self.epgView.top = globalControl.getPosition()
        self.epgView.right = self.epgView.left + globalControl.getWidth()
        self.epgView.bottom = self.epgView.top + globalControl.getHeight()
        self.epgView.width = globalControl.getWidth()
        self.epgView.cellHeight = globalControl.getHeight() / settings.getDisplayChannelsCount()
        
        start_time = datetime.datetime.now()
        self.epgView.start_time = start_time.replace(minute=(0 if start_time.minute <= 29 else 30))
        self.epgView.stop_time = self.epgView.start_time + datetime.timedelta(minutes=settings.getTimelineToDisplay() - 2)
        
        self.setEPGBackgrounds() 
        self.setTimesLabels()
        self.setTimeMarker(timer=True)
        
        database, cursor = connectEpgDB()
        self.epgDb  = EPGXML.EpgDb(database, cursor)
        self.epgXml = EPGXML.EpgXml(database, cursor, progress_bar=False)
        
        self.epgView.globalGrid = self.epgDb.getEpgGrid()
        self.epgView.setChannels()
        self.epgView.setFocus(0, 0)
    
    
    '''
    Set the EPG background with customer settings.
    '''
    def setEPGBackgrounds(self):
        
        bg = self.getControl(EPGControl.image.BACKGROUND)
        custombg = settings.useCustomBackground()
        bg_img = settings.getImageBackgroundCustom() if custombg else settings.getImageBackground()
        bg.setImage(bg_img, useCache=False) 
        self.getControl(EPGControl.image.TIME_MARKER).setImage(settings.getImageTimeMarker(), useCache=False)
    
    
    '''
    Set the time marker position
    '''
    def setTimeMarker(self, timer=False):
        
        tm = self.getControl(EPGControl.image.TIME_MARKER)
        dt_now = datetime.datetime.now()
        delta = dt_now - self.epgView.start_time
        tm.setVisible(False) 
        
        if delta.seconds >=  0 and delta.seconds <= settings.getTimelineToDisplay() * 60:
            x = self.epgView.secondsToX(delta.seconds)
            tm.setPosition(int(x), tm.getY())
            tm.setVisible(True)
                 
        if timer and not xbmc.abortRequested and not self.is_closing:
            Timer(1, self.setTimeMarker, {timer: True}).start()   
    
    
    '''
    Return the time turned into EPG style
    '''
    def setTimesLabels(self):
        
        def __toTimeView(ctime, multiplier):
            # Defining time for program guide and time labels zone.            
            increment = int(settings.getTimelineToDisplay() / 4) * multiplier
            later = (ctime + dt.timedelta(minutes=increment)).time()
            return str(("[B]%02d:%02d[/B]") % (later.hour, later.minute))

        #Setting date and time controls.
        lTime1 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_ONE)
        lTime2 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_TWO)
        lTime3 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_THREE)
        lTime4 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_FOUR)
        
        lTime1.setLabel(__toTimeView(self.epgView.start_time, 0))
        lTime2.setLabel(__toTimeView(self.epgView.start_time, 1))
        lTime3.setLabel(__toTimeView(self.epgView.start_time, 2))
        lTime4.setLabel(__toTimeView(self.epgView.start_time, 3))
        
        labelCurrentDate = self.getControl(EPGControl.label.DATE_TIME_TODAY)
        labelCurrentDate.setLabel(self.epgView.start_time.strftime("[B]%d/%m/%Y[/B]"))
    
        
    
    
    
    '''
    @overrided
    Handle all xbmc action messages.
    '''
    def onAction(self, action):

        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
            self.is_closing = True
            self.close()
            
        if action in [ACTION_MOVE_DOWN, ACTION_MOUSE_WHEEL_DOWN, ACTION_MOVE_UP, 
                      ACTION_MOUSE_WHEEL_UP, ACTION_MOVE_RIGHT, ACTION_MOVE_LEFT]:
            
            delta = datetime.timedelta(minutes=settings.getTimelineToDisplay())
            
            if action == ACTION_MOVE_LEFT :
                if self.epgView.previous() == False:
                    y = self.epgView.current_y
                    self.epgView.stop_time -= delta
                    self.epgView.start_time -= delta
                    self.epgView.setChannels() 
                    self.epgView.setFocus(0, y)     
                    
            elif action == ACTION_MOVE_RIGHT:
                if self.epgView.next() == False:
                    y = self.epgView.current_y
                    self.epgView.stop_time += delta
                    self.epgView.start_time += delta
                    self.epgView.setChannels()   
                    self.epgView.setFocus(0, y)
                    
            elif action in [ACTION_MOVE_UP, ACTION_MOUSE_WHEEL_UP]:
                if self.epgView.up() == False:
                    if self.epgView.start_channel_id - settings.getDisplayChannelsCount() < 0:
                        self.epgView.start_channel_id = 0
                    else:
                        self.epgView.start_channel_id -= settings.getDisplayChannelsCount()
                    self.epgView.setChannels()
                    self.epgView.setFocus(0, settings.getDisplayChannelsCount() - 1)
        
            elif action in [ACTION_MOVE_DOWN, ACTION_MOUSE_WHEEL_DOWN]:
                if self.epgView.down() == False:
                    if (self.epgView.start_channel_id + settings.getDisplayChannelsCount()) > (self.epgView.getChannelsCount() - settings.getDisplayChannelsCount()):
                        self.epgView.start_channel_id = self.epgView.getChannelsCount() - settings.getDisplayChannelsCount() 
                    else:
                        self.epgView.start_channel_id += settings.getDisplayChannelsCount()
                    self.epgView.setChannels()
                    self.epgView.setFocus(0,0)
                
            self.setTimesLabels()
        

    '''
    @overrided
    Handle all controls clicks, provide a control ID
    '''
    def onClick(self, controlID):
        pass
        
       
    '''
    @overrided
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
        