import xbmc

'''
Display a basic notification
    '''    
def notify(addon, message, plus=None):
    n_time  = '10000'
    n_title = 'Super Favourites XMLTV'
    n_logo  = addon.getAddonInfo('icon')
    message = addon.getLocalizedString(message)
    
    xbmc.log(message, xbmc.LOGERROR)
    if not plus is None:
        xbmc.log(plus, xbmc.LOGERROR)
        
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)'%(n_title, message, n_time, n_logo))
    
    

'''
Unzip given file taking care of compression type.
'''
def unzip(file, dest):
    pass