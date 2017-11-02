import os, sys, time
import datetime as dt
import urlparse
import xbmcvfs, xbmc, xbmcplugin, xbmcaddon, xbmcgui  

from resources.lib import EPGXML



'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    
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
    
    start_time = 0
        
    '''
    Class init.
    '''    
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        self.start_time = dt.datetime.today()
        
    
    '''
    @overrided
    Gui values init.
    '''
    def onInit(self):
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
            

''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''    
    
# Basic addons information.
addonid      = 'plugin.program.super.favourites.xmltv'
settings     = xbmcaddon.Addon(addonid)
    
EPGgui = XMLWindowEPG('epg.xml', settings.getAddonInfo('path'))
EPGgui.doModal()
    
del EPGgui