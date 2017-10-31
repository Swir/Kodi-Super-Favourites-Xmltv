import os
import sys
import urllib

import xbmcgui


class EPGList(object):
    
    list = []
    
    def __init__(self, *args, **kwargs):
        self.list = None
        
        
    def getList(self):
        return self.list   


def getEPGControlsList():
    epg_data = EPGList()
    return epg_data.getList()