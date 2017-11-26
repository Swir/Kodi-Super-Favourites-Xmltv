# -*- coding: utf-8 -*-
import time, datetime
import datetime as dt
import xbmc, xbmcgui  

from threading import Timer
from os.path import join

from resources.lib import EPGXML, superfavourites
from resources.lib.EPGCtl import EPGControl, EPGGridView
from resources.lib import strings, settings
from resources.lib.utils import connectEpgDB, strToDatetime

'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    DEBUG = True
    
    database = None
    cursor = None
    
    epgDb = None
    epgXml = None
    epgView = None
    
    # Customizable controls
    CHANNELS_ON_PAGE = 9
    MAXIMUM_TIME_PROGRAMS_DISPLAY = 120
    
    # Predefined const.
    BACKGROUND_BUILTIN = 'true'
    
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
        
        self.epgView = EPGGridView()
        self.epgView.left, self.epgView.top = globalControl.getPosition()
        self.epgView.right = self.epgView.left + globalControl.getWidth()
        self.epgView.bottom = self.epgView.top + globalControl.getHeight()
        self.epgView.width = globalControl.getWidth()
        self.epgView.cellHeight = globalControl.getHeight() / XMLWindowEPG.CHANNELS_ON_PAGE
        
        start_time = datetime.datetime.now()
        start_time_view = self.setTimesLabels(str(start_time.hour) + ":" + str(start_time.minute), halfInc=False)
        self.epgView.start_time = start_time.replace(hour=int(start_time_view[:2]), minute=int(start_time_view[3:]))
        
        self.setEPGBackgrounds() 
        self.setTimeMarker(timer=True)
        
        # Setting current day date.
        labelCurrentDate = self.getControl(EPGControl.label.DATE_TIME_TODAY)
        labelCurrentDate.setLabel(time.strftime("%d/%m/%Y"))
        
        #Setting date and time controls.
        labelTime1 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_ONE)
        labelTime2 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_TWO)
        labelTime3 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_THREE)
        labelTime4 = self.getControl(EPGControl.label.DATE_TIME_QUARTER_FOUR)
        
        labelTime1.setLabel(start_time_view)
        labelTime2.setLabel(self.setTimesLabels(labelTime1.getLabel()))
        labelTime3.setLabel(self.setTimesLabels(labelTime2.getLabel()))
        labelTime4.setLabel(self.setTimesLabels(labelTime3.getLabel()))
        
        self.database, self.cursor = connectEpgDB()
        self.epgDb  = EPGXML.EpgDb(self.database, self.cursor)
        self.epgXml = EPGXML.EpgXml(self.database, self.cursor, progress_bar=False)
        
        dt_stop = self.epgView.start_time + datetime.timedelta(minutes=self.MAXIMUM_TIME_PROGRAMS_DISPLAY - 2)
        self.setChannels(self.epgView.start_time, dt_stop)
    
    
    '''
    Set the EPG background with customer settings.
    '''
    def setEPGBackgrounds(self):
        
        bg = self.getControl(EPGControl.image.BACKGROUND)
        
        background_type = settings.addon.getSetting('type.background')
        
        if str(background_type) == XMLWindowEPG.BACKGROUND_BUILTIN:

            background = settings.addon.getSetting('image.background')
        
            if background == '' or background == None: 
                bg.setImage(settings.getAddonBackgroundsPath() + '1.jpg', useCache=False)
            elif int(background) == 0:
                bg.setImage(settings.getAddonBackgroundsPath() + '-transparent.png', useCache=False)
            else:
                bg.setImage(settings.getAddonBackgroundsPath() + background + '.jpg', useCache=False)
        else:
            bg_image = settings.addon.getSetting('custom.background')   
            bg.setImage(bg_image, useCache=False)  
            
    
    
    '''
    Set the time marker position
    '''
    def setTimeMarker(self, timer=False):
        
        tm = self.getControl(EPGControl.image.TIME_MARKER)
        dt_now = datetime.datetime.now()
        delta = dt_now - self.epgView.start_time
        tm.setVisible(False) 
        
        if delta.seconds >=  0 and delta.seconds <= XMLWindowEPG.MAXIMUM_TIME_PROGRAMS_DISPLAY * 60:
            x = self.epgView.secondsToX(delta.seconds)
            tm.setPosition(int(x), tm.getY())
            tm.setVisible(True)
                 
        if timer and not xbmc.abortRequested and not self.is_closing:
            Timer(1, self.setTimeMarker, {timer: True}).start()   
    
    
    '''
    Return the time turned into EPG style
    '''
    def setTimesLabels(self, currentDT, halfInc=True):
        # Defining time for program guide and time labels zone.
        hours = currentDT[0:currentDT.find(':')]
        mins  =  currentDT[currentDT.find(':') + 1 :]
        mins = '00' if int(mins) <= 29 else '30'
        
        current = dt.time(int(hours), int(mins))
        if halfInc:
            later = (dt.datetime.combine(dt.date.today(), current) + dt.timedelta(minutes=30)).time()
        else:
            later = current
        
        return str(("%02d:%02d") % (later.hour, later.minute))
    
    
    '''
    Sets first channels lines.
    '''
    def setChannels(self, dt_start, dt_stop):
        
        EPG = self.epgDb.getEpgGrid(dt_start, dt_stop)
        
        noFocusTexture = join(settings.getAddonImagesPath(), 'buttons', 'tvguide-program-grey.png')
        focusTexture = join(settings.getAddonImagesPath(), 'buttons', 'tvguide-program-grey-focus.png')
        
        idx = 0
        for channel in EPG.values():
            self.getControl(EPGControl.label.CHANNEL_LABEL_START + idx).setLabel(channel["display_name"])    
            # Program details.
            programs = channel["programs"]
            
            if len(programs) == 0:
                nothing = "No data available"
                pbutton = xbmcgui.ControlButton(
                    self.epgView.left, 
                    self.epgView.top + self.epgView.cellHeight * idx, 
                    self.epgView.right - self.epgView.left - 2, 
                    self.epgView.cellHeight - 2, 
                    nothing, focusTexture, noFocusTexture)
                self.addControl(pbutton)
                  
            for program in programs: 
                
                program_start = strToDatetime(program["start"])    
                program_end   = strToDatetime(program["end"])            
                
                deltaStart = program_start - self.epgView.start_time
                deltaStop  = program_end - self.epgView.start_time
                
                y = self.epgView.top + self.epgView.cellHeight * idx
                x = self.epgView.secondsToX(deltaStart.seconds)
                
                if deltaStart.days < 0:
                    x = self.epgView.left
                
                width = self.epgView.secondsToX(deltaStop.seconds) - x
                
                if x + width > self.epgView.right:
                    width = self.epgView.right - x
                width -= 2
                
                pbutton = xbmcgui.ControlButton(
                    x,y,
                    width,
                    self.epgView.cellHeight - 2,
                    program["title"],
                    noFocusTexture=noFocusTexture,
                    focusTexture=focusTexture
                )            
                self.addControl(pbutton)                        
            idx += 1
        
    
    '''
    @overrided
    Handle all xbmc action messages.
    '''
    def onAction(self, action):
        
        # Same as normal python Windows.
        if action == xbmcgui.ACTION_PREVIOUS_MENU:
            self.is_closing = True
            self.close()
        
        # Select an EPG line into the window
        #if action == xbmcgui.ACTION_MOUSE_LEFT_CLICK or action == xbmcgui.ACTION_SELECT_ITEM:
        #    pass


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
        pass    
        
            

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
        