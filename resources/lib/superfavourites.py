# -*- coding: utf-8 -*-
from os import mkdir
from os.path import isfile, join, exists
from xbmcgui import DialogProgress
from sqlite3 import Error as SqliteError
import xbmcgui
import xbmc
from xml.dom import minidom
from resources.lib.strings import SF_DIR_STRING, SF_CHANNELS_INFOS_ERROR
from resources.lib.strings import SF_SUBFOLDERS_PROGRESS_HEADER, SF_SUBFOLDERS_PROGRESS_MSG
from resources.lib.strings import ACTIONS_QUIT_WINDOW, ACTIONS_SELECT_STREAM, ACTIONS_NO_LINKS_FOUND
from resources.lib.utils import notify, connectEpgDB
from resources.lib.EPGXML import EpgDb
from resources.lib.settings import DEBUG, getSFFolder, getSFFoldersPattern, AddonConst

from xbmcaddon import Addon
import sys
import re


'''
Handle Super favourites iptv subfolders.
'''
class SuperFavouritesIptvFolder(object):
            
    epg_db = database = cursor = None 
     
    '''
    Init
    '''
    def __init__(self):
        self.database, self.cursor = connectEpgDB()
        self.epg_db = EpgDb(self.database, self.cursor)
    
     
    '''
    Create the base subfolders structure.
    '''
    def createSubFolders(self):
        progress = DialogProgress()
        try:
            progress.create(SF_SUBFOLDERS_PROGRESS_HEADER, SF_SUBFOLDERS_PROGRESS_MSG)
            row = "id_channel" if getSFFoldersPattern() == AddonConst.SF_XMLTV_ID_PATTERN else 'display_name' 
            request = "SELECT %s FROM channels" % row
            
            if self.database is None or self.cursor is None:
                notify(SF_CHANNELS_INFOS_ERROR)
                progress.close()
                return
            
            self.cursor.execute(request)
            channels = self.cursor.fetchall()
            
            i = 1
            for channel in channels:
                
                if not isfile(join(getSFFolder(translate=True), channel[0])):
                    try:
                        mkdir(join(getSFFolder(translate=True), channel[0]))
                    except OSError:
                        pass
                    
                progress.update(int( ( i / float(len(channels)) ) * 100), "", 
                                SF_DIR_STRING + ' %i/%i' % (i, len(channels)))
                i += 1
                
        except SqliteError:
            progress.close()
            if DEBUG:
                notify(SF_CHANNELS_INFOS_ERROR)
        progress.close()   
        
        
    '''
    Return the subfolder of given iptv channel.
    '''
    def getSubFolderLinks(self, id_channel):
        try:
            # Getting pattern
            channel_data = []
            row = "id_channel" if getSFFoldersPattern() == AddonConst.SF_XMLTV_ID_PATTERN else "display_name"
            request = 'SELECT %s FROM channels WHERE id=%i' % (row, id_channel)
            self.cursor.execute(request)
            pattern = self.cursor.fetchone()[0]
            
            sf_folder = join(xbmc.translatePath(getSFFolder()), pattern)
            
            if exists(sf_folder):
                xml_file = join(sf_folder, "favourites.xml")
                if exists(xml_file):
                    xml = minidom.parse(xml_file)
                    links = xml.getElementsByTagName("favourite")
                    
                    for link in links:
                        link_name   = link.getAttribute("name")
                        link_action = link.firstChild.nodeValue
                        channel_data.append({"name":link_name, "action":link_action})
                    return channel_data
                else:
                    return []
            else:
                return []
        except SqliteError:
            return []
        return []
    
    
    '''
    Cose the database oject
    '''
    def close(self):
        try:
            self.database.close()
            del self.cursor
            del self.database
        except:
            pass
        
        
        
class SuperFavouritesXMLDialog(xbmcgui.WindowXMLDialog):
    
    
    id_channel = 0
    logo_channel = None
    sfiptv = None
    iptv_links = []
    container = None
    
    ADDON   = Addon('plugin.program.super.favourites.xmltv')
    ADDONID = 'plugin.program.super.favourites.xmltv'
    PLAYMEDIA_MODE      = 1
    ACTIVATEWINDOW_MODE = 2
    RUNPLUGIN_MODE      = 3
    ACTION_MODE         = 4
    
    '''
    Init
    '''
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
    
    
    '''
    On init
    '''
    def onInit(self):
        self.container = self.getControl(50)
        self.getControl(5000).setLabel(ACTIONS_SELECT_STREAM)
        self.getControl(5001).setLabel(ACTIONS_QUIT_WINDOW)
        self.sfiptv = SuperFavouritesIptvFolder()
        self.iptv_links = self.sfiptv.getSubFolderLinks(self.id_channel)
        
        
        if not self.iptv_links is None and len(self.iptv_links) == 0 :
            self.getControl(50).setVisible(False)
            self.getControl(5000).setLabel(ACTIONS_NO_LINKS_FOUND)
        else:
            self.container.reset()
            for link in self.iptv_links:
                
                item = xbmcgui.ListItem(label=link["name"], iconImage=self.logo_channel)
                self.container.addItem(item)
                
        
    '''
    Set the channel ID
    '''
    def setChannel(self, id_channel, logo):
        self.id_channel = id_channel
        self.logo_channel = logo
        
    
    '''
    On window action
    '''   
    def onAction(self, action):
        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
            self.container.reset()
            self.close() 
        
        if action in [xbmcgui.ACTION_MOVE_LEFT, xbmcgui.ACTION_MOVE_RIGHT, ]:
            self.setFocus(self.getControl(5001))
        
        if action == xbmcgui.ACTION_SELECT_ITEM:
            itemPos = self.container.getSelectedPosition()
            if itemPos is not None and itemPos != -1:
                #xbmc.executebuiltin(self.iptv_links[itemPos]["action"])
                self.playCommand(self.iptv_links[itemPos]["action"])
                
                
    
    '''
    On controls clicks
    '''
    def onClick(self, controlId):
        if controlId == 5001:
            self.container.reset()
            self.close()
        
        




    def removeSFOptions(self, cmd):
        if 'sf_options=' not in cmd:
            return cmd

        cmd = cmd.replace('?sf_options=', '&sf_options=')

        cmd = re.sub('&sf_options=(.+?)_options_sf"\)', '")',               cmd)
        cmd = re.sub('&sf_options=(.+?)_options_sf",return\)', '",return)', cmd)
        cmd = re.sub('&sf_options=(.+?)_options_sf',    '',                 cmd)

        cmd = cmd.replace('/")', '")')

        return cmd


    def tidy(self, cmd):
        cmd = cmd.replace('&quot;', '')
        cmd = cmd.replace('&amp;', '&')
        cmd = self.removeSFOptions(cmd)
    
        if cmd.startswith('RunScript'):
            cmd = cmd.replace('?content_type=', '&content_type=')
            cmd = re.sub('/&content_type=(.+?)"\)', '")', cmd)
    
        if cmd.endswith('/")'):
            cmd = cmd.replace('/")', '")')
    
        if cmd.endswith(')")'):
            cmd = cmd.replace(')")', ')')
    
        return cmd
    


    def playCommand(self, originalCmd, contentMode=False):
        try:
            xbmc.executebuiltin('Dialog.Close(busydialog)') #Isengard fix
    
            cmd = self.tidy(originalCmd)
    
            #if in contentMode just do it
            if contentMode:
                xbmc.executebuiltin('ActivateWindow(Home)') #some items don't play nicely if launched from wrong window
                if cmd.lower().startswith('activatewindow'):
                    cmd = cmd.replace('")', '",return)') #just in case return is missing                
                return xbmc.executebuiltin(cmd)  
    
            if 'ActivateWindow' in cmd:
                return self.activateWindowCommand(cmd) 
    
            if 'PlayMedia' in cmd:
                return self.playMedia(originalCmd)
    
            if cmd.lower().startswith('executebuiltin'):
                try:    
                    cmd = cmd.split('"', 1)[-1]
                    cmd = cmd.rsplit('")')[0]
                except:
                    pass
    
            xbmc.executebuiltin(cmd)


        except Exception, e:
            pass   




    def activateWindowCommand(self, cmd):
        cmds = cmd.split(',', 1)
    
        #special case for filemanager
        if '10003' in cmds[0] or 'filemanager' in cmds[0].lower():
            xbmc.executebuiltin(cmd)
            return   
    
        plugin   = None
        activate = None
    
        if len(cmds) == 1:
            activate = cmds[0]
        else:
            activate = cmds[0]+',return)'
            plugin   = cmds[1][:-1]
    
        #check if it is a different window and if so activate it
        id = str(xbmcgui.getCurrentWindowId())    
    
        if id not in activate:
            xbmc.executebuiltin(activate)
    
        if plugin: 
            xbmc.executebuiltin('Container.Update(%s)' % plugin)


    def getSFOptions(self, cmd):
        import urllib 
    
        try:    options = urllib.unquote_plus(re.compile('sf_options=(.+?)_options_sf').search(cmd).group(1))
        except: return {}
    
        return self.get_params(options)
    
    

    def getOption(self, cmd, option):
        options = self.getSFOptions(cmd)
    
        try:    return options[option]
        except: return ''


    def playMedia(self, original): 
        cmd = self.tidy(original).replace(',', '') #remove spurious commas
        
        try:    mode = int(self.getOption(original, 'mode'))
        except: mode = 0
    
        if mode == self.PLAYMEDIA_MODE:       
            xbmc.executebuiltin(cmd)
            return
    
        plugin = re.compile('"(.+?)"').search(cmd).group(1)
    
        if len(plugin) < 1:
            xbmc.executebuiltin(cmd)
            return
    
        if mode == self.ACTIVATEWINDOW_MODE:   
            try:    winID = int(self.getOption(original, 'winID'))
            except: winID = 10025
    
            #check if it is a different window and if so activate it
            id = xbmcgui.getCurrentWindowId()
    
            if id != winID :
                xbmc.executebuiltin('ActivateWindow(%d)' % winID)
                
            cmd = 'Container.Update(%s)' % plugin
    
            xbmc.executebuiltin(cmd)
            return
    
        if mode == self.RUNPLUGIN_MODE:
            cmd = 'RunPlugin(%s)' % plugin
    
            xbmc.executebuiltin(cmd)
            return
    
        #if all else fails just execute it
        xbmc.executebuiltin(cmd)  
        
        
    def get_params(self, p):
        param=[]
        paramstring=p
        if len(paramstring)>=2:
            params=p
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param  
        
        
    