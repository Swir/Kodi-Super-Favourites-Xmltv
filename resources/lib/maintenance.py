# -*- coding: utf-8 -*-
import xbmc
from xbmcgui import Dialog
from os.path import join, isfile
from os import remove
from sys import argv


xbmc.log("Maintenance asked", xbmc.LOGERROR)

ACTION_HARD_RESET  = 0
ACTION_SF_FOLDERS = 1

try:
    action = int(argv[1])
    cwd = argv[2]
    path = cwd.replace('addons', join('userdata', 'addon_data'), 1)
    
    if action == ACTION_HARD_RESET:
        xbmc.log("Hard reset requested", xbmc.LOGERROR)
        db = join(path, "epg.db") 
        xmltv = join(path, "epg.xml") 
        
        if isfile(db):
            remove(db) 
        
        if isfile(xmltv):
            remove(xmltv)
        
        if not isfile(db) and not isfile(xmltv):
            Dialog().ok("Super Favourites XMLTV", "Hard Reset Ok !")
        else:
            Dialog().ok("Super Favourites XMLTV", "Hard Reset error !")
    
    elif action == ACTION_SF_FOLDERS:
        xbmc.log("Super Favourites folder remove request", xbmc.LOGERROR)
        
except Exception as e:
    xbmc.log("[SFX] " + e.message, xbmc.LOGERROR)