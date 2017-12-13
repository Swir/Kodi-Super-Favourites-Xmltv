# -*- coding: utf-8 -*-
try:
    from resources.lib import settings as plugin
except ImportError:
    import settings as plugin
    

DIALOG_TITLE         = plugin.addon.getLocalizedString(31001)
UNEXPECTED_EXCEPTION = plugin.addon.getLocalizedString(31002)
DEBUG_HEADER         = plugin.addon.getLocalizedString(31003)

# Settings -> Toolbox actions feedback
HARD_RESET_OK         = plugin.addon.getLocalizedString(300011)
HARD_RESET_NOK        = plugin.addon.getLocalizedString(300012)
HARD_RESET_FOLDERS_OK = plugin.addon.getLocalizedString(300013)

# Database messages
DB_CONNECTION_ERROR        = plugin.addon.getLocalizedString(300001)
DB_CREATE_TABLES_ERROR     = plugin.addon.getLocalizedString(300002)
DB_STATE_ERROR             = plugin.addon.getLocalizedString(300003)
DB_CHANNELS_TRUNCATE_ERROR = plugin.addon.getLocalizedString(300004)
DB_PROGRAMS_TRUNCATE_ERROR = plugin.addon.getLocalizedString(300005)

# Progress bars.
SF_SUBFOLDERS_PROGRESS_HEADER = plugin.addon.getLocalizedString(300021)
SF_SUBFOLDERS_PROGRESS_MSG    = plugin.addon.getLocalizedString(300022)
SF_CHANNELS_INFOS_ERROR       = plugin.addon.getLocalizedString(300023)    
SF_DIR_STRING                 = plugin.addon.getLocalizedString(300024)
SFX_EPG_UPDATE_HEADER         = plugin.addon.getLocalizedString(300025)
SFX_DOWNLOADING_MSG           = plugin.addon.getLocalizedString(300026)
SFX_LONG_TIME_MSG             = plugin.addon.getLocalizedString(300027)
SFX_CHANNEL                   = plugin.addon.getLocalizedString(300028)
SFX_PROGRAM                   = plugin.addon.getLocalizedString(300029)
SFX_ICONS_DOWNLOAD            = plugin.addon.getLocalizedString(300030)
SFX_ICON                      = plugin.addon.getLocalizedString(300031)


# HTTP Errors
HTTP_UNCHANGED_REMOTE_FILE = plugin.addon.getLocalizedString(300031)
HTTP_MOVED_PERMANENTLY     = plugin.addon.getLocalizedString(300032)
HTTP_BAD_REQUEST           = plugin.addon.getLocalizedString(300033)
HTTP_UNAUTHORIZED          = plugin.addon.getLocalizedString(300034)
HTTP_NOT_FOUND             = plugin.addon.getLocalizedString(300035)
HTTP_INTERNAL_SERVER_ERROR = plugin.addon.getLocalizedString(300036)
HTTP_BAD_GATEWAY           = plugin.addon.getLocalizedString(300037)
HTTP_SERVER_OVERLOADED     = plugin.addon.getLocalizedString(300038)
HTTP_REQUEST_TIMEOUT       = plugin.addon.getLocalizedString(300039)
HTTP_UNHANDLED_ERROR       = plugin.addon.getLocalizedString(3000310)
HTTP_DOWNLOAD_LOGO_ERROR   = plugin.addon.getLocalizedString(3000311)

# Zip / Tar archives.
ARCHIVE_UNSUPPORTED_FORMAT   = plugin.addon.getLocalizedString(300041)
ARCHIVE_ZIP_UNCOMPRESS_ERROR = plugin.addon.getLocalizedString(300042)
ARCHIVE_TAR_UNCOMPRESS_ERROR = plugin.addon.getLocalizedString(300043)
ARCHIVE_NO_XMLTV_FOUND       = plugin.addon.getLocalizedString(300044)

# Updates / install / cleanup
REGISTER_UPDATE_ERROR       = plugin.addon.getLocalizedString(300051)
LAST_UPDATE_NOT_FOUND       = plugin.addon.getLocalizedString(300052)
CLEANUP_PROGRAMS_ERROR      = plugin.addon.getLocalizedString(300053)
BAD_XMLTV_FILE_TYPE         = plugin.addon.getLocalizedString(300054)
XMLTV_FILE_NOT_FOUND        = plugin.addon.getLocalizedString(300055)
XMLTV_LOAD_ERROR            = plugin.addon.getLocalizedString(300056)
XMLTV_NO_URL_PROVIDED       = plugin.addon.getLocalizedString(300057)
XMLTV_NO_FILE_PROVIDED      = plugin.addon.getLocalizedString(300058)
NO_SUPER_FAVOURITES_FOLDER  = plugin.addon.getLocalizedString(300059)
BAD_ADDON_CONFIGURATION     = plugin.addon.getLocalizedString(3000510)
CONFIGURATION_TAKE_TIME_MSG = plugin.addon.getLocalizedString(3000511)
SFX_FIRST_START_DETECTED    = plugin.addon.getLocalizedString(3000512)
SFX_INIT_OK                 = plugin.addon.getLocalizedString(3000513)


# EPG Data
GET_CHANNELS_ERROR         = plugin.addon.getLocalizedString(300061)
GET_CHANNEL_PROGRAMS_ERROR = plugin.addon.getLocalizedString(300062)
GET_PROGRAM_ERROR          = plugin.addon.getLocalizedString(300063)
REMOVE_PROGRAM_ERROR       = plugin.addon.getLocalizedString(300064)
UPDATE_PROGRAM_ERROR       = plugin.addon.getLocalizedString(300065)
ADDING_PROGRAM_ERROR       = plugin.addon.getLocalizedString(300066)
GET_CHANNEL_ERROR          = plugin.addon.getLocalizedString(300067)
REMOVE_CHANNEL_ERROR       = plugin.addon.getLocalizedString(300068)
UPDATE_CHANNEL_ERROR       = plugin.addon.getLocalizedString(300069)
ADDING_CHANNEL_ERROR       = plugin.addon.getLocalizedString(3000610)
PROGRAM_NO_INFOS           = plugin.addon.getLocalizedString(3000611)

# Edit window actions
ACTIONS_QUIT_WINDOW    = plugin.addon.getLocalizedString(40001)
ACTIONS_RENAME_CHANNEL = plugin.addon.getLocalizedString(40002)
ACTIONS_HIDE_CHANNEL   = plugin.addon.getLocalizedString(40003)
ACTIONS_EDIT_CHANNEL   = plugin.addon.getLocalizedString(40004)
ACTIONS_LOGO_UPDATE    = plugin.addon.getLocalizedString(40005)
ACTIONS_PROGRAM_START  = plugin.addon.getLocalizedString(40006)
ACTIONS_PROGRAM_REMIND = plugin.addon.getLocalizedString(40007)
ACTIONS_PROGRAM_LABEL  = plugin.addon.getLocalizedString(40008)


