# -*- coding: utf-8 -*-
from xbmcaddon import Addon
from xbmc import translatePath
from os.path import join
try:
    from resources.lib import strings
except ImportError:
    import strings


addon = Addon('plugin.program.super.favourites.xmltv')
DEBUG = True if addon.getSetting('debug.mode') == 'true' else False


''' ============================== '''
'''       Global addon infos       '''
''' ============================== '''

def checkMandatorySettings():
    
    # Checking xmltv type
    if getXMLTVSourceType() == AddonConst.XMLTV_SOURCE_URL:
        if not getXMLTVURLRemote():
            return False, strings.XMLTV_NO_URL_PROVIDED
            
    elif getXMLTVSourceType() == AddonConst.XMLTV_SOURCE_LOCAL:
        if not getXMLTVURLLocal() :
            return False, strings.XMLTV_NO_FILE_PROVIDED 
      
    if getSFFolder() == 'special://home':
        return False, strings.NO_SUPER_FAVOURITES_FOLDER
    
    return True, ""


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
def getSFFolder(translate=False):
    if not translate:
        return addon.getSetting("super.favourites.folder")
    return translatePath(addon.getSetting("super.favourites.folder"))


'''
Return the sub folders pattern to use for IPTV.
'''
def getSFFoldersPattern():
    try:
        return int(addon.getSetting('super.favourites.subfolders.pattern'))
    except ValueError:
        return AddonConst.SF_XMLTV_ID_PATTERN


'''
Return the sleep value before updating
'''
def getTimeSleep():
    return (1 * 1000)  


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
    return int(frequency) + 1 if not frequency is None or frequency == '' else 1


'''
Return the cleanup treshold in days.
'''
def getCleanupTreshold():
    treshold = addon.getSetting('cleanup.treshold')
    return int(treshold) + 1 if not treshold is None or treshold == '' else 1


'''
Return XMLTV source type from settings.
'''
def getXMLTVSourceType():
    return int(addon.getSetting("xmltv.source.type"))


'''
Return the local url defined in settings.
'''
def getXMLTVURLLocal():
    return addon.getSetting('xmltv.local.value')


'''
Return the remote url defined in settings.
'''
def getXMLTVURLRemote():
    return addon.getSetting('xmltv.url.value')


'''
Return True if XMLTV source is compressed.
'''
def isXMLTVCompressed():
    return True if addon.getSetting('xmltv.compressed') == 'true' else False


'''
Return True if user wants to use its custom background.
'''
def useCustomBackground():
    return not str(addon.getSetting('type.background')) == 'true'


'''
Return a built in background image based on a provided ID
'''
def getImageBackground():
    background = addon.getSetting('image.background')
        
    if background == '' or background == None: 
        return getAddonBackgroundsPath() + '1.jpg'
    elif int(background) == 0:
        return getAddonBackgroundsPath() + '-transparent.png'
            
    return getAddonBackgroundsPath() + background + '.jpg' 
            

'''
Return the current background custom image path.
'''
def getImageBackgroundCustom():
    return addon.getSetting('custom.background')


'''
Return how many channels to display
'''
def getDisplayChannelsCount():
    return int(addon.getSetting('channels.count'))


'''
Return the timeline length
'''
def getTimelineToDisplay():
    return int(addon.getSetting('timeline.count')) * 60


'''
Addon consts
'''
class AddonConst(object):
    # SF consts.
    SF_XMLTV_ID_PATTERN    = 0
    SF_DISPLAY_NAME_PATERN = 1
    
    # %aintenance consts ( hard reset )
    ACTION_HARD_RESET = 0
    ACTION_SF_FOLDERS = 1
    
    # XMLTV
    XMLTV_SOURCE_URL   = 0
    XMLTV_SOURCE_LOCAL = 1
    
    def __init__(self):
        pass
    
