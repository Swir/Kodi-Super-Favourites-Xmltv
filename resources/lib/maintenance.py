# -*- coding: utf-8 -*-
import xbmc
from xbmcgui import Dialog
from xbmcaddon import Addon
from os.path import join, isfile, isdir
from os import remove, listdir
from sys import argv
from shutil import rmtree


ACTION_HARD_RESET  = 0
ACTION_SF_FOLDERS = 1

try:
    action = int(argv[1])
    cwd = argv[2]
    path = cwd.replace('addons', join('userdata', 'addon_data'), 1)
    addon = Addon('plugin.program.super.favourites.xmltv')
    
    if action == ACTION_HARD_RESET:
        
        db = join(path, "epg.db") 
        db_journal = db + "-journal"
        xmltv = join(path, "epg.xml") 
        
        if isfile(db):
            remove(db) 
            if isfile(db_journal):
                remove(db_journal)
        
        if isfile(xmltv):
            remove(xmltv)
        
        if not isfile(db) and not isfile(xmltv):
            Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33904))
        else:
            Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33905))
    
    elif action == ACTION_SF_FOLDERS:
        super_favourites_folder = addon.getSetting("super.favourites.folder")
        super_favourites_folder = xbmc.translatePath(super_favourites_folder)
        
        for sfpath in listdir(super_favourites_folder):
            sfpath = join(super_favourites_folder, sfpath)
            
            if isdir(sfpath):
                xbmc.log("[SFX] " + sfpath, xbmc.LOGERROR)
                rmtree(sfpath, ignore_errors=True)
            else:
                remove(sfpath)
                
        Dialog().ok("Super Favourites XMLTV", addon.getLocalizedString(33906))
            
except Exception as e:
    xbmc.log("[SFX] Error: " + e.message, xbmc.LOGERROR)