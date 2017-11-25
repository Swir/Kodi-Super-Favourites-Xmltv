# -*- coding: utf-8 -*-
from xbmcgui import Dialog
from os.path import join, isfile, isdir
from os import remove, listdir
from sys import argv
from shutil import rmtree

from strings import HARD_RESET_OK, HARD_RESET_NOK, DIALOG_TITLE, HARD_RESET_FOLDERS_OK
from settings import AddonConst
from settings import getEpgDbFilePath, getEpgXmlFilePath, getSFFolder

try:
    if int(argv[1]) == AddonConst.ACTION_HARD_RESET:
        
        if isfile(getEpgDbFilePath()):
            remove(getEpgDbFilePath()) 
            if isfile(getEpgDbFilePath() + "-journal"):
                remove(getEpgDbFilePath() + "-journal")
        
        if isfile(getEpgXmlFilePath()):
            remove(getEpgXmlFilePath())
        
        if not isfile(getEpgDbFilePath()) and not isfile(getEpgXmlFilePath()):
            Dialog().ok(DIALOG_TITLE, HARD_RESET_OK)
        else:
            Dialog().ok(DIALOG_TITLE, HARD_RESET_NOK)
    
    elif int(argv[1]) == AddonConst.ACTION_SF_FOLDERS:
        
        for sfpath in listdir(getSFFolder(True)):
            sfpath = join(getSFFolder(True), sfpath)
            
            if isdir(sfpath):
                rmtree(sfpath, ignore_errors=True)
            else:
                remove(sfpath)
                
        Dialog().ok(DIALOG_TITLE, HARD_RESET_FOLDERS_OK)
            
except Exception:
    pass