import os, sys, time
import urlparse
import xbmcvfs, xbmc, xbmcplugin, xbmcaddon, xbmcgui  

from resources.lib import EPGXML



'''
Global class handling EPG Gui.
'''
class XMLWindowEPG(xbmcgui.WindowXMLDialog):
    
    # XML gui structure.
    
        
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)


    def onInit(self):
        pass



    def onAction(self, action):
        
        # Same as normal python Windows.
        if action == xbmcgui.ACTION_PREVIOUS_MENU:
            xbmc.sleep(500)
            self.close()
        
        # Select an EPG line into the window
        #if action == xbmcgui.ACTION_MOUSE_LEFT_CLICK or action == xbmcgui.ACTION_SELECT_ITEM:
        #    pass



    def onClick(self, controlID):
        pass
        
       

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