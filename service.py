# -*- coding: utf-8 -*-
import xbmc
from resources.lib.update import ThreadedUpdater
from resources.lib.strings import DEBUG_HEADER, UNEXPECTED_EXCEPTION

try:
    # Updater object
    epg_updater = ThreadedUpdater()
    epg_updater.start()
except Exception, ex:
    xbmc.log('%s %s: %s' % (DEBUG_HEADER, UNEXPECTED_EXCEPTION , str(ex)) , xbmc.LOGDEBUG)