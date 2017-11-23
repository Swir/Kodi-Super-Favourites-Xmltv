# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
from resources.lib.update import ThreadedUpdater


try:
    addon = xbmcaddon.Addon(id = 'plugin.program.super.favourites.xmltv')
    # Updater object
    epg_updater = ThreadedUpdater(addon)
    epg_updater.start()
except Exception, ex:
    xbmc.log('[SF XMLTV] Unhandled exception in service.py: %s' % str(ex) , xbmc.LOGDEBUG)