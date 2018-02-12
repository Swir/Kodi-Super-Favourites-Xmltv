# -*- coding: utf-8 -*-
from xbmcaddon import Addon
from xbmc import translatePath
from os import mkdir
from os.path import join, exists
from datetime import timedelta
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
    try:
        if getXMLTVSourceType() == AddonConst.XMLTV_SOURCE_URL:
            if not getXMLTVURLRemote():
                return False, strings.XMLTV_NO_URL_PROVIDED
                
        elif getXMLTVSourceType() == AddonConst.XMLTV_SOURCE_LOCAL:
            if not getXMLTVURLLocal() :
                return False, strings.XMLTV_NO_FILE_PROVIDED 
          
        if getSFFolder() == 'special://profile':
            return False, strings.NO_SUPER_FAVOURITES_FOLDER
    except ValueError:
        return False, ""
        
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
    path = join(translatePath("special://profile/addon_data"), "plugin.program.super.favourites.xmltv")
    if not exists(path):
        mkdir(path)    
    return path


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
Return the channels logos path
'''
def getChannelsLogoPath():
    return join(getAddonUserDataPath(), "logos")



'''
Return tables structures
'''
def getTablesStructure():
    channels  = "CREATE TABLE channels (id INTEGER PRIMARY KEY AUTOINCREMENT, id_channel TEXT, display_name TEXT, logo TEXT, source TEXT, visible BOOLEAN)"
    programs  = "CREATE TABLE programs (id_program INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, start_date TEXT, end_date TEXT, description TEXT)"
    updates   = "CREATE TABLE updates (id_update INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP)"  
    reminders = "CREATE TABLE reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, id_program INTEGER)"  

    return channels, programs, updates, reminders



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
Return True to auto create Super Favourites IPTV Folders.
'''
def autoCreateSFFolders():
    try:
        return True if addon.getSetting("super.favourites.subfolders.create") == "true" else False
    except:
        return False


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
        
    if background == '' or background is None: 
        return getAddonBackgroundsPath() + '1.jpg'
    elif int(background) == 0:
        return getAddonBackgroundsPath() + '-transparent.png'
            
    return getAddonBackgroundsPath() + background + '.jpg' 


'''
Return the time marker image as configured in settings.
'''
def getImageTimeMarker():
    
    timebars = join(getAddonImagesPath(), 'timebars')
    marker = addon.getSetting('image.timemarker')
    
    if marker == '' or marker is None: 
        marker = '0'
            
    return join(timebars, "timebar-" + marker + ".png")
            

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
Return true if epg will use the xmltv logo
'''
def useXMLTVSourceLogos():
    return True if addon.getSetting('xmltv.logos') == 'true' else False

'''
Return true if we will use thetvdblogo as channels icons source
'''
def useTheTvDBSourceLogos():
    return True if addon.getSetting('thetvdb.logos') == 'true' else False


'''
Return the maximum 'previous' number of days to load from the programs db
'''
def getMaxPrevLoad():
    load = addon.getSetting('prev.load')
    return abs( (int(load) + 1 if not load is None or load == '' else 1) - 7) + 1


'''
Return the maximum 'next' number of days to load from the programs db
'''
def getMaxNextLoad():
    load = addon.getSetting('next.load')
    return abs( (int(load) + 1 if not load is None or load == '' else 1) - 7) + 1


'''
Return true if programs reminders are enabled
'''
def useProgramsReminder():
    return True if addon.getSetting('reminders.enabled') == 'true' else False


'''
Return the selected time for notifications
'''
def getRemindersTime():
    settings_time = addon.getSetting('reminders.time')
    settings_time = int(settings_time) + 1 if not settings_time is None or settings_time == '' else 1
    
    return timedelta(minutes=(settings_time * 15))


'''
Return the no focus texture
'''
def getNoFocusTexture():
    return join(getAddonImagesPath(), 'buttons', 'program-grey.png')


'''
Return the focus texture
'''
def getFocusTexture():
    return join(getAddonImagesPath(), 'buttons', 'program-grey-focus.png')


'''
Return the no focus texture
'''
def getReminderNoFocusTexture():
    return join(getAddonImagesPath(), 'buttons', 'program-red.png')


'''
Return the focus texture
'''
def getReminderFocusTexture():
    return join(getAddonImagesPath(), 'buttons', 'program-red-focus.png')


'''
Return true if user want to adjust time with timezone setting.
'''
def useTimeZone():
    return True if addon.getSetting('timezone.enabled') == 'true' else False


'''
Return the delta representing the timezone setting value.
'''
def getTimeZoneDelta():
    
    return timedelta(hours=int(addon.getSetting("timezone.value")))


'''
Return timezone action.
'''
def getTimeZoneOperation():
    action = addon.getSetting('timezone.action')
    return int(action) if not action is None or action == '' else 0



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
    ACTION_DELETE_REMINDERS = 2
    
    # XMLTV
    XMLTV_SOURCE_URL   = 0
    XMLTV_SOURCE_LOCAL = 1
    
    TIMEZONE_ADD = 0
    TIMEZONE_SUB = 1
    
    def __init__(self):
        pass
    
