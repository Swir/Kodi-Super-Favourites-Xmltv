# -*- coding: utf-8 -*-
from xbmcaddon import Addon
from xbmc import translatePath
from os.path import join


addon = Addon('plugin.program.super.favourites.xmltv')

''' ============================== '''
'''       Global addon infos       '''
''' ============================== '''

'''
Return the addon path
'''
def getAddonPath(translated=False):
    if not translated:
        return addon.getAddonInfo('path')
    return translatePath(addon.getAddonInfo('path'))


'''
Return the addin image path.
'''
def getAddonImagesPath():
    return join(getAddonPath(),'resources', 'skins', 'Default', 'media')


'''
Return the addon background images path.
'''
def getAddonBackgroundsPath():
    return join(getAddonImagesPath(), 'backgrounds', 'bg')


'''
Return the userdata related to the addon.
''' 
def getAddonUserDataPath():
    return getAddonPath(True).replace('addons', join('userdata', 'addon_data'), 1)


'''
Return the epg db file location.
'''
def getEpgDbFilePath():
    return join(getAddonUserDataPath(), "epg.db")


'''
Return the epg xml file location
'''
def getEpgXmlFilePath():
    return join(getAddonUserDataPath(), "epg.xml")


'''
Return the addon icon
'''
def getAddonIcon():
    return addon.getAddonInfo('icon')



'''
Return tables structures
'''
def getTablesStructure():
    channels = "CREATE TABLE channels (id INTEGER PRIMARY KEY AUTOINCREMENT, id_channel TEXT, display_name TEXT, logo TEXT, source TEXT, visible BOOLEAN)"
    programs = "CREATE TABLE programs (id_program INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, start_date TEXT, end_date TEXT, description TEXT)"
    updates  = "CREATE TABLE updates (id_update INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP)"  
    return channels, programs, updates



''' ============================== '''
'''   Settings from settings.xml   '''
''' ============================== '''

'''
Return Super Favourites iptv folder from settings.
'''
def getSuperFavouritesFolder(translated=False):
    if not translated:
        return addon.getSetting("super.favourites.folder")
    return translatePath(addon.getSetting("super.favourites.folder"))


'''
Return true for startup updates.
'''
def doStartupUpdate():
    return True if addon.getSetting('startup.update') == 'true' else False


'''
Return the update frequency
'''
def getUpdateFrequency():
    frequency = addon.getSetting('update.frequency')
    return int(frequency) + 1 if not frequency is None else 1
