# -*- coding: utf-8 -*-
import time, datetime
import datetime as dt
import xbmc, xbmcaddon, xbmcgui  

from threading import Timer
from os.path import join

from resources.lib import EPGXML, superfavourites, utils
from resources.lib.EPGCtl import EPGControl, EPGGridView



'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    DEBUG = True
    
    epg_view = None
    database = None
    cursor = None
    
    epg_db = None
    epg_xml = None
    epg_grid = None
    
    # Customizable controls
    CHANNELS_ON_PAGE = 9
    
    '''
     For futures versions skinings.
    '''
    #Set the maximum time of the timeline..
    MAXIMUM_TIME_PROGRAMS_DISPLAY = 120
    
    # Channels labels ( not content )
    CHANNEL_LABEL_START = 4010
    CHANNEL_LOGO_START   = 4110
    PROGRAM_TITLE = 4020
    
    # Predefined const.
    BACKGROUND_BUILTIN = 'true'
    
    addon_id = 'plugin.program.super.favourites.xmltv'
    addon = None
    addon_path = None
    addon_bg_base = None
    addon_images = None
    is_closing = False
        
    '''
    Class init.
    '''    
    def __init__(self, strXMLname, strFallbackPath):
        self.addon = xbmcaddon.Addon(self.addon_id)
        
        self.addon_path = addon.getAddonInfo('path')
        self.addon_images = join(self.addon_path,'resources', 'skins', 'Default', 'media')
        self.addon_bg_base = join(self.addon_images, 'backgrounds', 'bg')
        
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        
    
    '''
    @overrided
    Gui values init.
    '''
    def onInit(self):
        
        # Init EPG Grid global View
        globalControl = self.getControl(EPGControl.GLOBAL_CONTROL)
        
        self.epg_view = EPGGridView()
        self.epg_view.left, self.epg_view.top = globalControl.getPosition()
        self.epg_view.right = self.epg_view.left + globalControl.getWidth()
        self.epg_view.bottom = self.epg_view.top + globalControl.getHeight()
        self.epg_view.width = globalControl.getWidth()
        self.epg_view.cellHeight = globalControl.getHeight() / XMLWindowEPG.CHANNELS_ON_PAGE
        
        start_time = datetime.datetime.now()
        start_time_view = self.setTimesLabels(str(start_time.hour) + ":" + str(start_time.minute), halfInc=False)
        self.epg_view.start_time = start_time.replace(hour=int(start_time_view[:2]), minute=int(start_time_view[3:]))
        
        
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
        
        # DB object
        self.epg_db = EPGXML.EpgDb(addon, self.DEBUG)
        self.database, self.cursor = utils.connectEpgDB(self.epg_db, self.addon)   
        self.epg_db.setDatabaseObj(self.database)
        self.epg_db.setCursorObj(self.cursor)
        
        # XMLTV object
        self.epg_xml = EPGXML.EpgXml(self.addon, self.DEBUG, progress_bar=False)
        self.epg_xml.setDatabaseObj(self.database)
        self.epg_xml.setCursorObj(self.cursor)
        
        self.setChannels(0)
    
    
    '''
    Set the EPG background with customer settings.
    '''
    def setEPGBackgrounds(self):
        
        bg = self.getControl(EPGControl.image.BACKGROUND)
        
        background_type = self.addon.getSetting('type.background')
        
        if str(background_type) == XMLWindowEPG.BACKGROUND_BUILTIN:

            background = self.addon.getSetting('image.background')
        
            if background == '' or background == None: 
                bg.setImage(self.addon_bg_base + '1.jpg', useCache=False)
            elif int(background) == 0:
                bg.setImage(self.addon_bg_base + '-transparent.png', useCache=False)
            else:
                bg.setImage(self.addon_bg_base + background + '.jpg', useCache=False)
        else:
            bg_image = self.addon.getSetting('custom.background')   
            bg.setImage(bg_image, useCache=False)  
            
    
    
    '''
    Set the time marker position
    '''
    def setTimeMarker(self, timer=False):
        
        tm = self.getControl(EPGControl.image.TIME_MARKER)
        dt_now = datetime.datetime.now()
        delta = dt_now - self.epg_view.start_time
        tm.setVisible(False) 
        
        if delta.seconds >=  0 and delta.seconds <= XMLWindowEPG.MAXIMUM_TIME_PROGRAMS_DISPLAY * 60:
            x = self.epg_view.secondsToX(delta.seconds)
            tm.setPosition(int(x), tm.getY())
            tm.setVisible(True)
                 
        if timer and not xbmc.abortRequested and not self.is_closing:
            Timer(1, self.setTimeMarker, {timer: True}).start()   
    
    
    '''
    Return the time turned into EPG style
    '''
    def setTimesLabels(self, currentDT, halfInc=True):
        # Defining time for program guide and time labels zone.
        index = currentDT.find(':')
        
        hours = currentDT[0:index]
        mins  =  currentDT[index + 1 :]
        
        if int(mins) <= 29:
            mins = '00'
        else:
            mins = '30'
        
        current = dt.time(int(hours), int(mins))
        if halfInc:
            later = (dt.datetime.combine(dt.date.today(), current) + dt.timedelta(minutes=30)).time()
        else:
            later = current
        
        return str(("%02d:%02d") % (later.hour, later.minute))
    
    
    
    '''
    Sets first channels lines.
    '''
    def setChannels(self, start):
        
        dt_stop = self.epg_view.start_time + datetime.timedelta(minutes=self.MAXIMUM_TIME_PROGRAMS_DISPLAY - 2)
        
        EPG = self.epg_db.getEpgGrid(self.epg_view.start_time, dt_stop)
        
        noFocusTexture = join(self.addon_images, 'buttons', 'tvguide-program-grey.png')
        focusTexture = join(self.addon_images, 'buttons', 'tvguide-program-grey-focus.png')
        
        idx = 0
        for channel in EPG.values():
            self.getControl(XMLWindowEPG.CHANNEL_LABEL_START + idx).setLabel(channel["display_name"])    
            # Program details.
            programs = channel["programs"]
            
            if len(programs) == 0:
                nothing = "No data available"
                pbutton = xbmcgui.ControlButton(
                    self.epg_view.left, 
                    self.epg_view.top + self.epg_view.cellHeight * idx, 
                    self.epg_view.right - self.epg_view.left - 2, 
                    self.epg_view.cellHeight - 2, 
                    nothing, focusTexture, noFocusTexture)
                self.addControl(pbutton)
                  
            for program in programs:                 
                try:
                    program_start = datetime.datetime.strptime(program["start"], "%Y%m%d%H%M%S")
                    program_end = datetime.datetime.strptime(program["end"], "%Y%m%d%H%M%S")
                except TypeError:
                    program_start = datetime.datetime(*(time.strptime(program["start"], "%Y%m%d%H%M%S")[0:6]))
                    program_end = datetime.datetime(*(time.strptime(program["end"], "%Y%m%d%H%M%S")[0:6]))
                
                deltaStart = program_start - self.epg_view.start_time
                deltaStop  = program_end - self.epg_view.start_time
                
                y = self.epg_view.top + self.epg_view.cellHeight * idx
                x = self.epg_view.secondsToX(deltaStart.seconds)
                
                if deltaStart.days < 0:
                    x = self.epg_view.left
                
                width = self.epg_view.secondsToX(deltaStop.seconds) - x
                
                if x + width > self.epg_view.right:
                    width = self.epg_view.right - x
                width -= 2
                
                pbutton = xbmcgui.ControlButton(
                    x,y,
                    width,
                    self.epg_view.cellHeight - 2,
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
            xbmc.sleep(500)
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
def checkSettings(addon): # TODO  ----------------------------------------------------
    settings_ok = True
    error_msg   = ''
    
    # Checking xmltv type
    if int(addon.getSetting('xmltv.source.type')) == 0:
        if not addon.getSetting('xmltv.url.value'):
            settings_ok = False
            error_msg = addon.getLocalizedString(33302)
            
    elif int(addon.getSetting('xmltv.source.type')) == 1:
        if not addon.getSetting('xmltv.local.value') :
            settings_ok = False
            error_msg = addon.getLocalizedString(33304)
      
    # Checking Super Favourites settings    
    sp_folder = addon.getSetting('super.favourites.folder')   
    if sp_folder == 'special://home':
        settings_ok = False
        error_msg = addon.getLocalizedString(33305)
    
    return settings_ok, error_msg
    



if __name__ == '__main__':
    addon = xbmcaddon.Addon('plugin.program.super.favourites.xmltv')
    
    # Checking for bad configuration.   
    ok, error_msg = checkSettings(addon)
    
    # Checking if some settings were completed.
    if not ok:
        title      = addon.getLocalizedString(33301)
        conclusion = addon.getLocalizedString(33303)
        xbmcgui.Dialog().ok(addon.getAddonInfo('name'), title, error_msg, conclusion)
        addon.openSettings()
    
    else:      
        debug = True if addon.getSetting('debug.mode') == 'true' else False
        epg_db = EPGXML.EpgDb(addon, debug)
        database, cursor = utils.connectEpgDB(epg_db, addon)   
        epg_db.setDatabaseObj(database)
        epg_db.setCursorObj(cursor)
        
        # Populate and create tables in case of first start
        if epg_db.firstTimeRuning():
            xbmcgui.Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33422))
            epg_xml = EPGXML.EpgXml(addon, debug, progress_bar=True)
            epg_xml.setDatabaseObj(database)
            epg_xml.setCursorObj(cursor)
            epg_xml.getXMLTV()
            
            xbmc.sleep(1500)
            epg_db.setFirstTimeRuning(0)
            epg_db.setUpdateDate()
            epg_db.getCleanOld()
            
            # Super favourites folder init.
            sf_folder = superfavourites.SuperFavouritesIptvFolder(addon)
            sf_folder.createSubFolders()
            
            # All is done, restart required
            xbmcgui.Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33421))
            
            xbmc.sleep(1000)
            sf_folder.close()
            epg_db.close()
            epg_xml.close()
            del epg_db
            del epg_xml
            
            
        # Else, update epg in a thread
        else:
            # Starting GUI
            EPGgui = XMLWindowEPG('epg.xml', addon.getAddonInfo('path'))
            EPGgui.doModal() 
            del EPGgui        
        