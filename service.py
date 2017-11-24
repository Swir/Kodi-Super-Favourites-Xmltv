# -*- coding: utf-8 -*-
import xbmc
from resources.lib.update import ThreadedUpdater
from resources.lib import strings

try:
    # Updater object
    epg_updater = ThreadedUpdater()
    epg_updater.start()
except Exception, ex:
    xbmc.log('%s %s: %s' % (strings.DEBUG_HEADER, strings.UNEXPECTED_EXCEPTION , str(ex)) , xbmc.LOGDEBUG)