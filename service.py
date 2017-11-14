# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
from resources.lib import EPGXML, utils


try:
    addon = xbmcaddon.Addon(id = 'plugin.program.super.favourites.xmltv')
    if addon.getSetting('startup.update') == 'true':
        # Updater object
        epg_updater = utils.ThreadedUpdater(addon)
        epg_updater.start()
except Exception, ex:
    xbmc.log('[SF XMLTV] Uncaugt exception in service.py: %s' % str(ex) , xbmc.LOGDEBUG)