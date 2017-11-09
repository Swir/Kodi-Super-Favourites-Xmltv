import xbmc

'''
Display a basic notification
    '''    
def notify(addon, message):
    n_time  = '10000'
    n_title = 'Super Favourites XMLTV'
    n_logo  = addon.getAddonInfo('icon')
    message = addon.getLocalizedString(message)
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)'%(n_title, message, n_time, n_logo))