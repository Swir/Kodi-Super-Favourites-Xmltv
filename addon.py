import os, sys, time
import urlparse
import xbmcvfs, xbmc, xbmcplugin, xbmcaddon, xbmcgui  

from resources.lib import EPGXML



class EPGAddonWindow(xbmcgui.WindowDialog):
    
    channels_list = [];
    
    # Layout purpose.
    base_factor = 100
    y_factor    = 50
        
    def __init__(self, channels_list_data, *args, **kwargs):  
        
        if channels_list_data != None and len(channels_list_data) > 0:
            self.channels_list = channels_list_data
            
        # Base layout.
        self.addControl(xbmcgui.ControlImage(0, 0, 1300, 720, 'special://home//addons//plugin.program.super.favourites.xmltv//resources//media//background.jpg'))      

        # For gui tests purpose only.
        self.__addTestsControls()

        if len(self.channels_list) > 0 :
            for i in self.channels_list:
                self.addControl(i)



    def onAction(self, action):
        # Close the current window
        if action == xbmcgui.ACTION_PREVIOUS_MENU:
            self.close()
        
        # Select an EPG line into the window
        if action == xbmcgui.ACTION_MOUSE_LEFT_CLICK or action == xbmcgui.ACTION_SELECT_ITEM:
            pass


    def onControl(self, control):
        if control == self.list:
            item = self.list.getSelectedItem()
            self.message('You selected : ' + item.getLabel())
            self.close()



    def message(self, message):
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        
    
    
    # The only goal of this function is to test the graphical layout, it will be commented out later on.
    def __addTestsControls(self):
        self.button0 = xbmcgui.ControlButton(-450, 100, 2200, 100, 'Web TV 1', alignment=6)
        self.addControl(self.button0)

        self.button1 = xbmcgui.ControlButton(-450, 150, 2200, 100, 'Web TV 2', alignment=6)
        self.addControl(self.button1)

        self.button2 = xbmcgui.ControlButton(-450, 200, 2200, 100, 'Web TV 3', alignment=6)
        self.addControl(self.button2)

        self.button3 = xbmcgui.ControlButton(-450, 250, 2200, 100, 'Web TV 4', alignment=6)
        self.addControl(self.button3)

        self.button4 = xbmcgui.ControlButton(-450, 300, 2200, 100, 'Web TV 5', alignment=6)
        self.addControl(self.button4)
        
                

''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''    
    

def main():
    
    # Basic addons information.
    addonid      = 'plugin.program.super.favourites.xmltv'
    settings     = xbmcaddon.Addon(addonid)
    addonName    = settings.getAddonInfo('name')
    addonVersion = settings.getAddonInfo('version')
    addonHandle  = int(sys.argv[1])
    
    # Getting arguments.
    params = urlparse.parse_qs('&'.join(sys.argv[1:]))
    
    # Gettinh EPG xml files infos
    epg_list = EPGXML.getEPGControlsList()
    
    # Creatin EPG window
    epg_window = EPGAddonWindow(epg_list, **params)
    epg_window.doModal()
    del epg_window


if __name__ == '__main__':
    main()

