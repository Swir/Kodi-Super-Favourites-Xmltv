# -*- coding: utf-8 -*-
from xbmcgui import Dialog
from os.path import join, isfile, isdir
from os import remove, listdir
from sys import argv
from shutil import rmtree

import settings, strings


ACTION_HARD_RESET  = 0
ACTION_SF_FOLDERS = 1

try:
    action = int(argv[1])
    
    if action == ACTION_HARD_RESET:
        
        db = settings.getEpgDbFilePath() 
        db_journal = db + "-journal"
        xmltv = settings.getEpgXmlFilePath() 
        
        if isfile(db):
            remove(db) 
            if isfile(db_journal):
                remove(db_journal)
        
        if isfile(xmltv):
            remove(xmltv)
        
        if not isfile(db) and not isfile(xmltv):
            Dialog().ok(strings.DIALOG_TITLE, strings.HARD_RESET_OK)
        else:
            Dialog().ok(strings.DIALOG_TITLE, strings.HARD_RESET_NOK)
    
    elif action == ACTION_SF_FOLDERS:
        super_favourites_folder = settings.getSuperFavouritesFolder(True)
        
        for sfpath in listdir(super_favourites_folder):
            sfpath = join(super_favourites_folder, sfpath)
            
            if isdir(sfpath):
                rmtree(sfpath, ignore_errors=True)
            else:
                remove(sfpath)
                
        Dialog().ok(strings.DIALOG_TITLE, strings.HARD_RESET_FOLDERS_OK)
            
except Exception:
    pass