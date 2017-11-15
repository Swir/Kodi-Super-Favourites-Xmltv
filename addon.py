# -*- coding: utf-8 -*-
import time
import datetime as dt
import xbmc, xbmcaddon, xbmcgui  

from resources.lib import EPGXML, utils, superfavourites


'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    DEBUG = True
    
    # XML gui structure.
    BACKGROUND_IMAGE = 4600
    
    # Date and time xml controls.
    DATE_TIME_TODAY_LABEL    = 4000
    DATE_TIME_FIRST_COLUMN  = 4001
    DATE_TIME_SECOND_COLUMN = 4002
    DATE_TIME_THIRD_COLUMN  = 4003
    DATE_TIME_FOURTH_COLUMN = 4004
    
    # Channels labels ( not content )
    CHANNEL_LABEL_1 = 4010
    CHANNEL_LABEL_2 = 4011
    CHANNEL_LABEL_3 = 4012
    CHANNEL_LABEL_4 = 4013
    CHANNEL_LABEL_5 = 4014
    CHANNEL_LABEL_6 = 4015
    CHANNEL_LABEL_7 = 4016
    CHANNEL_LABEL_8 = 4017
    CHANNEL_LABEL_9 = 4018
    
    # Channels logos
    CHANNEL_LOGO_1 = 4110
    CHANNEL_LOGO_2 = 4111
    CHANNEL_LOGO_3 = 4112
    CHANNEL_LOGO_4 = 4113
    CHANNEL_LOGO_5 = 4114
    CHANNEL_LOGO_6 = 4115
    CHANNEL_LOGO_7 = 4116
    CHANNEL_LOGO_8 = 4117
    CHANNEL_LOGO_9 = 4118
    
    # Predefined const.
    BACKGROUND_BUILTIN = 'true'
    
    start_time = 0
    addon_id = 'plugin.program.super.favourites.xmltv'
    addon_settings = None
    addon_path = None
    addon_bg_base = None
        
    '''
    Class init.
    '''    
    def __init__(self, strXMLname, strFallbackPath):
        self.addon_settings = xbmcaddon.Addon(self.addon_id)
        self.addon_path = addon.getAddonInfo('path')
        self.addon_bg_base = self.addon_path + '/resources/skins/Default/media/backgrounds/bg'
        
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        self.start_time = dt.datetime.today()
        
    
    '''
    @overrided
    Gui values init.
    '''
    def onInit(self):
        
        # Defining background
        self.setEPGBackground()
                        
        # Setting current day date.
        labelCurrentDate = self.getControl(XMLWindowEPG.DATE_TIME_TODAY_LABEL)
        labelCurrentDate.setLabel(time.strftime("%d/%m/%Y"))

        #Setting date and time controls.
        labelTime1 = self.getControl(XMLWindowEPG.DATE_TIME_FIRST_COLUMN)
        labelTime2 = self.getControl(XMLWindowEPG.DATE_TIME_SECOND_COLUMN)
        labelTime3 = self.getControl(XMLWindowEPG.DATE_TIME_THIRD_COLUMN)
        labelTime4 = self.getControl(XMLWindowEPG.DATE_TIME_FOURTH_COLUMN)
        
        labelTime1.setLabel(self.setTimesLabels(str(self.start_time.hour) + ":" + str(self.start_time.minute), halfInc=False))
        labelTime2.setLabel(self.setTimesLabels(labelTime1.getLabel()))
        labelTime3.setLabel(self.setTimesLabels(labelTime2.getLabel()))
        labelTime4.setLabel(self.setTimesLabels(labelTime3.getLabel()))
    
    
    '''
    Set the EPG background with customer settings.
    '''
    def setEPGBackground(self):
        
        bg = self.getControl(XMLWindowEPG.BACKGROUND_IMAGE)
        background_type = self.addon_settings.getSetting('type.background')
        
        if str(background_type) == XMLWindowEPG.BACKGROUND_BUILTIN:

            background = self.addon_settings.getSetting('image.background')
        
            if background == '' or background == None: 
                bg.setImage(self.addon_bg_base + '1.jpg', useCache=False)
            elif int(background) == 0:
                bg.setImage(self.addon_bg_base + '-transparent.png', useCache=False)
            else:
                bg.setImage(self.addon_bg_base + background + '.jpg', useCache=False)
        else:
            bg_image = self.addon_settings.getSetting('custom.background')   
            bg.setImage(bg_image, useCache=False)  
            
    
    
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
    @overrided
    Handle all xbmc action messages.
    '''
    def onAction(self, action):
        
        # Same as normal python Windows.
        if action == xbmcgui.ACTION_PREVIOUS_MENU:
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
            epg_db.setFirstTimeRuning(0)
            epg_db.setUpdateDate()
            
            del epg_db
            del epg_xml
            
            # Super favourites folder init.
            sf_folder = superfavourites.SuperFavouritesIptvFolder(addon)
            sf_folder.createSubFolders()
            
            # All is done, restart required
            xbmcgui.Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33421))
        # Else, update epg in a thread
        else:
            # Updater object
            epg_updater = utils.ThreadedUpdater(addon)
            epg_updater.start()
            
            # Starting GUI
            EPGgui = XMLWindowEPG('epg.xml', addon.getAddonInfo('path'))
            EPGgui.doModal() 
            del EPGgui        
        