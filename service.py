# -*- coding: utf-8 -*-
import xbmc
from resources.lib.update import ThreadedUpdater
from resources.lib.utils import ThreadedNotifier
from resources.lib.strings import DEBUG_HEADER, UNEXPECTED_EXCEPTION

try:
    # Updater object.
    epg_updater = ThreadedUpdater()
    # Notifier object.
    epg_notifier = ThreadedNotifier()
    
    epg_updater.start()
    epg_notifier.start()
    
except Exception, ex:
    xbmc.log('%s %s: %s' % (DEBUG_HEADER, UNEXPECTED_EXCEPTION , str(ex)) , xbmc.LOGDEBUG)