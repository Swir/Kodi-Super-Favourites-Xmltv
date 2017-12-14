# -*- coding: utf-8 -*-
import xbmcgui, xbmc
from os import rename, mkdir
from os.path import join, exists
from shutil import copy2 as copy
from uuid import uuid4
from datetime import timedelta, datetime
from threading import Timer
from xbmc import abortRequested
from resources.lib import settings
from resources.lib.EPGXML import EpgDb, TheLogoDbChannel
from resources.lib.utils import strToDatetime, connectEpgDB, notify
from resources.lib.strings import PROGRAM_NO_INFOS, ACTIONS_QUIT_WINDOW, \
     ACTIONS_RENAME_CHANNEL, ACTIONS_HIDE_CHANNEL, ACTIONS_EDIT_CHANNEL, \
     ACTIONS_LOGO_UPDATE, ACTIONS_PROGRAM_START, ACTIONS_PROGRAM_REMIND, \
     ACTIONS_PROGRAM_LABEL, EDIT_LOGO_HEADER, EDIT_LOGO_THE_LOGODB, \
     EDIT_LOGO_FROM_LOCAL, EDIT_LOGO_ERROR, EDIT_NO_LOGO_FOUND, DIALOG_TITLE, \
     SFX_ICONS_DOWNLOAD, EDIT_LOGOS_SEARCH, EDIT_CHOOSE_LOGO, EDIT_CHOOSE_FROM_SELECT

''' 
Handle View positions.
''' 

class EPGGridView(object):
    
    window = None
    
    globalGrid = []
    currentGrid = []
    labelControls = []
    
    current_x = 0
    current_y = 0
    current_control = None  
    is_closing = False
    isControlBox = False

    
    '''
    Defining grid view points.
    '''
    def __init__(self, window):
        self.window = window
        self.start_time = self.stop_time = None
        self.start_channel_id = 0
        
        globalControl = self.window.getControl(EPGControl.GLOBAL_CONTROL)
        self.left, self.top = globalControl.getPosition()
        self.right = self.left + globalControl.getWidth()
        self.bottom = self.top + globalControl.getHeight()
        self.width = globalControl.getWidth()
        self.cellHeight = globalControl.getHeight() / settings.getDisplayChannelsCount()
        
        self.noFocusTexture = join(settings.getAddonImagesPath(), 'buttons', 'tvguide-program-grey.png')
        self.focusTexture = join(settings.getAddonImagesPath(), 'buttons', 'tvguide-program-grey-focus.png')
        
        start_time = datetime.now()
        self.start_time = start_time.replace(minute=(0 if start_time.minute <= 29 else 30))
        self.stop_time = self.start_time + timedelta(minutes=settings.getTimelineToDisplay() - 2)
    
        self.setEPGBackgrounds()
        self.setTimeMarker(timer=True)
        self.setTimesLabels()         
        
    
    
    '''
    Set the EPG background with customer settings.
    '''
    def setEPGBackgrounds(self):
        
        bg = self.window.getControl(EPGControl.image.BACKGROUND)
        custombg = settings.useCustomBackground()
        bg_img = settings.getImageBackgroundCustom() if custombg else settings.getImageBackground()
        bg.setImage(bg_img, useCache=False) 
        self.window.getControl(EPGControl.image.TIME_MARKER).setImage(settings.getImageTimeMarker(), useCache=False)
       
    
    '''
    Set the time marker position
    '''
    def setTimeMarker(self, timer=False):
        
        tm = self.window.getControl(EPGControl.image.TIME_MARKER)
        dt_now = datetime.now()
        delta = dt_now - self.start_time
        tm.setVisible(False) 
        
        if delta.seconds >=  0 and delta.seconds <= settings.getTimelineToDisplay() * 60:
            x = self.secondsToX(delta.seconds)
            tm.setPosition(int(x), tm.getY())
            tm.setVisible(True)
                 
        if timer and not abortRequested and not self.is_closing:
            Timer(1, self.setTimeMarker, {timer: True}).start() 
            
            
    '''
    Return the time turned into EPG style
    '''
    def setTimesLabels(self):
        
        def __toTimeView(ctime, multiplier):
            # Defining time for program guide and time labels zone.            
            increment = int(settings.getTimelineToDisplay() / 4) * multiplier
            later = (ctime + timedelta(minutes=increment)).time()
            return str(("[B]%02d:%02d[/B]") % (later.hour, later.minute))

        #Setting date and time controls.
        lTime1 = self.window.getControl(EPGControl.label.DATE_TIME_QUARTER_ONE)
        lTime2 = self.window.getControl(EPGControl.label.DATE_TIME_QUARTER_TWO)
        lTime3 = self.window.getControl(EPGControl.label.DATE_TIME_QUARTER_THREE)
        lTime4 = self.window.getControl(EPGControl.label.DATE_TIME_QUARTER_FOUR)
        
        lTime1.setLabel(__toTimeView(self.start_time, 0))
        lTime2.setLabel(__toTimeView(self.start_time, 1))
        lTime3.setLabel(__toTimeView(self.start_time, 2))
        lTime4.setLabel(__toTimeView(self.start_time, 3))
        
        labelCurrentDate = self.window.getControl(EPGControl.label.DATE_TIME_TODAY)
        labelCurrentDate.setLabel(self.start_time.strftime("[B]%d/%m/%Y[/B]"))
            
            
    '''                            '''
    ''' Grid XBMC controls related '''
    ''' ___________________________'''    
    
    '''
    Sets grid as a list of controls
    y_grid as a list
    '''
    def append(self, y_grid):
        self.currentGrid.append(y_grid)
        self.reset()        
    
    
    '''
    Reset the control grid
    '''
    def reset(self, clear_grid=False):
        self.current_x = 0
        self.current_y = 0
        if clear_grid:
            self.clearGrid()
    
    
    '''
    Clear the current used grid
    '''
    def clearGrid(self):
        ctrls = [program["control"] for ctrl in self.currentGrid for program in ctrl]
        self.window.removeControls(ctrls)
        self.window.removeControls(self.labelControls)
        del self.currentGrid[:]
        del self.labelControls[:]
        self.labelControls = []
        self.currentGrid = []
        
        
        
    '''
    Set the focus to the given control coordonates.
    '''
    def setFocus(self, x, y):
        self.window.setFocus(self.currentGrid[y][x]["control"])   
    
    
    '''
    Return the current targeted channel id and channel name.
    '''
    def getChannel(self, x=None, y=None):
        x = x if not x is None else self.current_x
        y = y if not y is None else self.current_y
        return self.currentGrid[y][x]["cdb_id"], self.currentGrid[y][x]["cdisplay_name"]  
    
    
    '''
    Return the current targeted program basic infos : db id and title
    '''
    def getProgram(self, control):
        infos, x, y = self.getInfosFromCurrentGrid(control)
        return infos["db_id"], infos["title"]
    
    
    '''
    Return the focused control
    '''
    def getCurrentControl(self):
        return self.current_control
    
    
    
    '''
    Set the current program infos.
    '''
    def setInfos(self, controlID): 
        
        infos, self.current_y, self.current_x = self.getInfosFromCurrentGrid(controlID)
        
        if not infos is None:
            
            title = "[B]" + infos["title"] + "[/B]"
            self.window.getControl(EPGControl.label.PROGRAM_TITLE).setLabel(title) 
            self.window.getControl(EPGControl.label.PROGRAM_DESCRIPTION).setText(infos["desc"])
            if not infos["db_id"] is None:
                time = "[B]" + infos["start"].strftime("%H:%M") + " - " + infos["stop"].strftime("%H:%M") + "[/B]"
            else:
                time = "00:00 - 00:00"
            ctime = self.window.getControl(EPGControl.label.PROGRAM_TIME)
            ctime.setLabel(time) 
            
            self.window.getControl(EPGControl.label.CHANNEL_NAME).setLabel(self.currentGrid[self.current_y][self.current_x]["cdisplay_name"])
            logo = join(settings.getChannelsLogoPath(), self.currentGrid[self.current_y][self.current_x]["logo"])
            self.window.getControl(EPGControl.image.CHANNEL_LOGO).setImage(logo, False)
        
    
        
    '''
    Return control id informations.
    '''   
    def getInfosFromCurrentGrid(self, controlID):
        cy = -1
        for y in self.currentGrid:
            cy += 1
            for x in y:
                if x["control"].getId() == controlID:
                    return x, cy, y.index(x)
        return None, self.current_y, self.current_x
    
    
    '''
    Return True if the given control ID is a program control ID
    '''
    def isProgramControl(self, controlID):
        status, y, x = self.getInfosFromCurrentGrid(controlID)
        return status is not None
    
    
    '''
    Seconds from delta to x position
    '''
    def secondsToX(self, secs):
        return self.left + (secs * self.width / (settings.getTimelineToDisplay() * 60)) + 24
     
     
     
    '''                              '''
    ''' Grid Data from EPGdb related '''
    ''' _____________________________'''  
    
    '''
    Set the grid data to be displayed
    '''
    def setGlobalDataGrid(self, grid):
        self.globalGrid = grid
           
        
    '''
    Return channels count
    '''
    def getChannelsCount(self):
        return len(self.globalGrid)
        
    
    '''
    Return a grid portion based on channels count and programs time
    '''
    def __getGridPortion(self):
        
        def __removeDuplicates(plist):
            rem = []
            for i in range(len(plist)):
                for y in range(len(plist)):
                    if y != i and int(plist[y]["start"]) == int(plist[i]["start"]) : 
                        idx = i if int(plist[y]["end"]) > int(plist[i]["end"]) else y
                        if not idx in rem:
                            rem.append( idx ) 
                        break
            remrt = []
            for i in range(len(plist)):
                if not i in rem:
                    remrt.append(plist[i])
            return remrt
            
            
        grid = self.globalGrid[self.start_channel_id : self.start_channel_id + settings.getDisplayChannelsCount()]
        tbr = []
        for channel in grid:
            programs = []
            for program in __removeDuplicates(channel["programs"]):
                
                stop = strToDatetime(program["end"])
                start = strToDatetime(program["start"])
                
                if stop > self.start_time and start < self.stop_time:
                    programs.append(program)
            
            tbr.append({"db_id":channel["db_id"],"id_channel": channel["id_channel"], 
                        "display_name" : channel["display_name"], "programs": programs,
                        "logo" : channel["logo"]}) 
        return tbr

        
    
    '''                              '''
    '''     Grid user manipulation   '''
    ''' _____________________________''' 
    
    '''
    Sets channels lines
    '''
    def displayChannels(self):
        self.reset(clear_grid=True)
        EPG_page = self.__getGridPortion() 
        
        gridControls = []
        idx = 0
        for channel in EPG_page:            
            y = self.top + self.cellHeight * idx + int((self.cellHeight / 14))
            
            if not settings.useXMLTVSourceLogos():
                pchannel = xbmcgui.ControlLabel(16, y + 2, 180, self.cellHeight - 8, "[B]" + channel["display_name"] + "[/B]")
            else:
                logo = channel["logo"]
                
                if logo != "" and logo is not None:
                    logo = join(settings.getChannelsLogoPath(), logo)
                    if exists(logo):
                        pchannel = xbmcgui.ControlImage(16, y + 2, 170, self.cellHeight - 8, logo, aspectRatio=2)
                    else:
                        pchannel = xbmcgui.ControlLabel(16, y + 2, 180, self.cellHeight - 8, "[B]" + channel["display_name"] + "[/B]")
                else:
                    pchannel = xbmcgui.ControlLabel(16, y + 2, 180, self.cellHeight - 8, "[B]" + channel["display_name"] + "[/B]")
 
            gridControls.append(pchannel)
            self.labelControls.append(pchannel)
                        
            # Program details.
            controls_x_grid = []
            programs = channel["programs"]
            
            if len(programs) == 0:
                
                pbutton = xbmcgui.ControlButton(
                    self.left, self.top + self.cellHeight * idx, 
                    self.right - self.left - 2, self.cellHeight - 2, 
                    PROGRAM_NO_INFOS, self.focusTexture, self.noFocusTexture)
                
                gridControls.append(pbutton)
                controls_x_grid.append({"db_id": None, "desc": PROGRAM_NO_INFOS, 
                                        "title": PROGRAM_NO_INFOS, "start": None, 
                                        "stop":  None, "control": pbutton,
                                        "cdisplay_name":channel["display_name"],
                                        "cdb_id":channel["db_id"], "logo":channel["logo"]})
            for program in programs: 
                
                program_start = strToDatetime(program["start"])    
                program_end   = strToDatetime(program["end"])            
                
                deltaStart = program_start - self.start_time
                deltaStop  = program_end - self.start_time
                
                y = self.top + self.cellHeight * idx
                x = self.secondsToX(deltaStart.seconds)
                
                if deltaStart.days < 0:
                    x = self.left
                
                width = self.secondsToX(deltaStop.seconds) - x
                
                if x + width > self.right:
                    width = self.right - x
                
                width -= 2
                
                if width < 28:
                    program["title"] = ""
                
                pbutton = xbmcgui.ControlButton(
                    x,y,width, self.cellHeight - 2, program["title"],
                    noFocusTexture=self.noFocusTexture, focusTexture=self.focusTexture
                )    
                
                gridControls.append(pbutton)  
                controls_x_grid.append({"db_id": program["db_id"], "desc": program["desc"], 
                                        "title": program["title"], "start": program_start, 
                                        "stop":  program_end, "control": pbutton,
                                        "cdisplay_name":channel["display_name"],
                                        "cdb_id":channel["db_id"], "logo":channel["logo"]})   
            self.append(controls_x_grid)                      
            idx += 1
            
        self.window.addControls(gridControls)
        
        
    '''
    Go to the next program control or next page.
    '''
    def next(self):
        if len(self.currentGrid[self.current_y]) - 1 == self.current_x:
            # Load new page
            delta = timedelta(minutes=settings.getTimelineToDisplay())
            y = self.current_y
            self.stop_time += delta
            self.start_time += delta
            self.displayChannels()   
            self.setFocus(0, y)
            self.setTimesLabels()
        else:
            # Next control
            self.current_x += 1
            self.setFocus(self.current_x, self.current_y)
    
    
    '''
    Go to the previous control or previous page.
    '''
    def previous(self):
        if self.current_x == 0:
            delta = timedelta(minutes=settings.getTimelineToDisplay())
            y = self.current_y
            self.stop_time -= delta
            self.start_time -= delta
            self.displayChannels() 
            self.setFocus(0, y)
            self.setTimesLabels()
        else:
            self.current_x -= 1
            self.setFocus(self.current_x, self.current_y)
    
    
    def up(self):
        if self.current_y == 0:
            if self.start_channel_id - settings.getDisplayChannelsCount() < 0:
                self.start_channel_id = 0
            else:
                self.start_channel_id -= settings.getDisplayChannelsCount()
            self.displayChannels()
            self.setFocus(0, settings.getDisplayChannelsCount() - 1)
            self.setTimesLabels()
        else:
            self.current_y -= 1
            self.current_x = 0
            self.setFocus(self.current_x, self.current_y)
    
    
    def down(self):
        #xbmc.log(str(len(self.currentGrid)), xbmc.LOGERROR)
        if len(self.currentGrid) - 1 == self.current_y:
            if (self.start_channel_id + settings.getDisplayChannelsCount()) > (self.getChannelsCount() - settings.getDisplayChannelsCount()):
                self.start_channel_id = self.getChannelsCount() - settings.getDisplayChannelsCount() 
            else:
                self.start_channel_id += settings.getDisplayChannelsCount()
            self.displayChannels()
            self.setFocus(0,0)
            self.setTimesLabels()
        else:
            self.current_y += 1
            self.current_x = 0
            self.setFocus(self.current_x, self.current_y)
                       

'''
Hansle splash screen loading image in case of large xmltv files
'''
class SplashScreen(object):
    
    def __init__(self, window, viewWidth, viewHeight):
        self.window = window
        
        x = int(viewWidth / 2) + int(193 / 4)
        y = int(viewHeight / 2) + int(192 / 4)
        
        img = join(settings.getAddonImagesPath(), "splashscreen", "loading.gif")
        bg = join(settings.getAddonImagesPath(), "splashscreen", "splash-bg.png")
        
        self.splash = xbmcgui.ControlImage(x, y, int(193 / 2), int(192 / 2), img)
        self.splashBg = xbmcgui.ControlImage(0, 0, viewWidth * 2, viewHeight * 2, bg)
              

    '''
    Display slashscreen
    '''
    def start(self):
        self.window.addControl(self.splashBg)
        self.window.addControl(self.splash)
        
    
    '''
    Removes the splah screen.
    '''
    def stop(self):
        self.window.removeControl(self.splashBg)
        self.window.removeControl(self.splash)


   
    
'''
Edit channel popup window
'''
class EditWindow(xbmcgui.WindowXMLDialog):
    
    program_title = display_name = ""
    program_id = id_channel = None
    titleLabel = programLabel = None
    parent = None
        
    def __init__(self, strXMLname, strFallbackPath):       
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)
        
    
    '''
    Window init.
    '''
    def onInit(self):
        xbmcgui.WindowXMLDialog.onInit(self)
        self.titleLabel = self.getControl(EditControls.CHANNEL_LABEL)
        self.titleLabel.setLabel(ACTIONS_EDIT_CHANNEL + "[CR]" + self.display_name)
        
        self.programLabel = self.getControl(EditControls.PROGRAM_LABEL)
        self.programLabel.setLabel(ACTIONS_PROGRAM_LABEL + "[CR]" + self.program_title)
        
        self.getControl(EditControls.CHANNEL_HIDE).setLabel(ACTIONS_HIDE_CHANNEL)
        self.getControl(EditControls.CHANNEL_RENAME).setLabel(ACTIONS_RENAME_CHANNEL)
        self.getControl(EditControls.QUIT).setLabel(ACTIONS_QUIT_WINDOW)
        self.getControl(EditControls.CHANNEL_LOGO_UPDATE).setLabel(ACTIONS_LOGO_UPDATE)
        self.getControl(EditControls.PROGRAM_START).setLabel(ACTIONS_PROGRAM_START)
        self.getControl(EditControls.PROGRAM_REMINDER).setLabel(ACTIONS_PROGRAM_REMIND)
        self.setFocus(self.getControl(EditControls.PROGRAM_START))


        
    '''
    Sets the target channel id and name
    '''
    def setChannel(self, c_id, c_name):
        self.display_name = c_name.decode("utf-8", 'ignore')
        self.id_channel = c_id
    
    
    '''
    Sets the target program id and title
    '''
    def setProgram(self, p_id, p_title):
        self.program_title = p_title.decode("utf-8", 'ignore')
        self.program_id = p_id
    
    
    '''
    Set the parent window
    '''
    def setParent(self, parentWindow):
        self.parent = parentWindow   
        
        
    '''
    Handle clicks actions.
    '''
    def onClick(self, controlId):
        self.titleLabel.setLabel(ACTIONS_EDIT_CHANNEL + "[CR]" + self.display_name)
        
        # Close
        if controlId == EditControls.QUIT:
            self.close()
        
        # Channel actions
        elif controlId in [EditControls.CHANNEL_HIDE, EditControls.CHANNEL_RENAME, 
                           EditControls.CHANNEL_LOGO_UPDATE]:
            database, cursor = connectEpgDB()
            epgDb = EpgDb(database, cursor)
            
            # Hide channel from EPG
            if controlId == EditControls.CHANNEL_HIDE:
                epgDb.updateChannel(self.id_channel, visible=False)
            
            # Rename the current channel.
            elif controlId == EditControls.CHANNEL_RENAME:
                new_name = xbmcgui.Dialog().input("ACTIONS_RENAME_TITLE", self.display_name)
                if not new_name is None or new_name == "":
                    epgDb.updateChannel(self.id_channel, display_name=new_name)
                    # renaming sf directory if 'display names' are used.
                    if not settings.getSFFoldersPattern() == settings.AddonConst.SF_XMLTV_ID_PATTERN:
                        joined = join(settings.getSFFolder(translate=True), self.display_name)
                        if exists(joined):
                            rename(joined, join(settings.getSFFolder(translate=True), new_name))
                        else:
                            mkdir(join(settings.getSFFolder(translate=True), new_name)) 
                        
                        self.display_name = new_name
                        self.titleLabel.setLabel(ACTIONS_EDIT_CHANNEL + "[CR]" + self.display_name)
 
            # Update channel logo
            elif controlId == EditControls.CHANNEL_LOGO_UPDATE:
                source = xbmcgui.Dialog().select(EDIT_LOGO_HEADER, [EDIT_LOGO_FROM_LOCAL, EDIT_LOGO_THE_LOGODB])    
                
                # Start local source dialog browser
                if source == 0:
                    n_logo = xbmcgui.Dialog().browse(2, EDIT_LOGO_HEADER, 'files')
                    if not n_logo is None:
                        name = str(uuid4()) + n_logo[n_logo.rfind(r".") :]
                        dest = join(settings.getChannelsLogoPath(), name)
                        try:
                            copy(n_logo, dest)
                            epgDb.updateChannel(self.id_channel, logo=name)
                        except:
                            if settings.DEBUG:
                                notify(EDIT_LOGO_ERROR)
                            del database
                            del cursor
                            epgDb.close()
                            del epgDb
                            return
                                
                # Start TheLogoDb search       
                elif source == 1:
                    thelogodb = TheLogoDbChannel(self.display_name)
                    if thelogodb.search():
                        progress = xbmcgui.DialogProgress()
                        progress.create(DIALOG_TITLE, SFX_ICONS_DOWNLOAD)
                        
                        # Display found logos.
                        logos = thelogodb.getLogos()
                        logos_local = []
                        win_logo = LogoEditWindowXML('logo-edit-window.xml', settings.getAddonPath())
                        
                        import ssl
                        from urllib2 import urlopen, HTTPError
                        from os.path import isdir
                        from shutil import rmtree
                        
                        ssl._create_default_https_context = ssl._create_unverified_context
                        dest_dir = join(xbmc.translatePath("special://home/temp"), "logos_tmp")
        
                        if not isdir(dest_dir):
                            mkdir(dest_dir) 
                        i = 1
                        for logo in logos:
                            progress.update(int( ( i / float(len(logos)) ) * 100), "", EDIT_LOGOS_SEARCH)
                            try:
                                if not logo is None:
                                    dest_file = join(dest_dir, logo[logo.rfind(r"/") + 1 :])
                                    download = urlopen(logo, timeout=30)
         
                                    tsf = open(dest_file, "w")
                                    tsf.write(download.read())
                                    tsf.close()
                                    del tsf   
                                    logos_local.append(dest_file)  
                                    i += 1                       
                            except HTTPError as e:
                                if e.code in [304, 301, 400, 401, 403, 404, 500, 502, 503, 504]:
                                    notify(EDIT_LOGO_ERROR)  
                                progress.close()      
                        
                        progress.close()
                        
                        win_logo.addToList(logos_local)  
                        win_logo.id_channel = self.id_channel                            
                        win_logo.doModal()
                        del win_logo
                        rmtree(dest_dir)
                         
                    else:
                        xbmcgui.Dialog().ok(EDIT_LOGO_HEADER, EDIT_NO_LOGO_FOUND)
                        
                             
            del database
            del cursor
            epgDb.close()
            del epgDb
            if not self.parent is None:
                self.parent.clear()
                self.parent.onInit()
        
        # Program actions.
        
        
'''
Create a window that can be use in many configuration situations.
'''
class LogoEditWindowXML(xbmcgui.WindowXMLDialog):
    
    list_items = None
    list_items_controls = None
    listItemsContainer = None
    id_channel = 0
    
    '''
    init
    '''
    def __init__(self, strXMLname, strFallbackPath):
        xbmcgui.WindowXML.__init__(self, strXMLname, strFallbackPath, default='Default', defaultRes='720p', isMedia=True)


    '''
    Gui init.
    '''
    def onInit(self):
        xbmcgui.WindowXMLDialog.onInit(self)
        self.getControl(5000).setLabel(EDIT_CHOOSE_LOGO)
        self.getControl(5001).setLabel(ACTIONS_QUIT_WINDOW)
        self.getControl(5002).setLabel(EDIT_CHOOSE_FROM_SELECT)
        self.listItemsContainer = self.getControl(50)
        self.listItemsContainer.addItems(self.list_items_controls)
        if len(self.list_items_controls) > 0:
            self.listItemsContainer.selectItem(0)
        
    
    '''
    Add items to items list
    ''' 
    def addToList(self, liste):
        self.list_items = []
        self.list_items_controls = []
        
        i = 1
        for item in liste:
            self.list_items.append(item)
            it = xbmcgui.ListItem(label="Logo " + str(i), iconImage=item)
            self.list_items_controls.append(it)
            i +=  1
            
    
    '''
    Handle onClick actions.
    '''    
    def onClick(self, controlId):
        if controlId == 5001:
            self.close()
        
        elif controlId == 5002:
            logo = self.list_items[self.getControl(50).getSelectedPosition()]
            if not logo is None:
                database, cursor = connectEpgDB()
                epgDb = EpgDb(database, cursor)
                
                name = str(uuid4()) + logo[logo.rfind(r".") :]
                dest = join(settings.getChannelsLogoPath(), name)
                try:
                    copy(logo, dest)
                    epgDb.updateChannel(self.id_channel, logo=name)
                except:
                    if settings.DEBUG:
                        notify(EDIT_LOGO_ERROR)
                    del database
                    del cursor
                    epgDb.close()
                    del epgDb
                    return
                self.close()
                
     
    '''
    Handle window exit
    '''   
    def onAction(self, action):
        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
            self.close() 
        
        if action in [xbmcgui.ACTION_MOVE_LEFT, xbmcgui.ACTION_MOVE_RIGHT, 
                      xbmcgui.ACTION_SELECT_ITEM, xbmcgui.ACTION_MOUSE_DOUBLE_CLICK]:
            self.setFocus(self.getControl(5002))
            

'''
Reference to EPG kodi controls.
'''
class EPGControl(object):
    
    GLOBAL_CONTROL = 5001
    
    '''
    Images references.
    '''
    class image(object):
        BACKGROUND = 4600
        TIME_MARKER = 4100
        CHANNEL_LOGO   = 4031
        
    '''
    Labels references
    '''
    class label(object):
        DATE_TIME_TODAY         = 4000
        DATE_TIME_QUARTER_ONE   = 4001
        DATE_TIME_QUARTER_TWO   = 4002
        DATE_TIME_QUARTER_THREE = 4003
        DATE_TIME_QUARTER_FOUR  = 4004
        
        PROGRAM_TITLE = 4020
        PROGRAM_DESCRIPTION = 4022
        PROGRAM_TIME = 4021
        
        CHANNEL_NAME   = 4030
    
'''
Edit window controls
'''
class EditControls(object):
        
    QUIT = 4002
    CHANNEL_HIDE   = 4000
    CHANNEL_RENAME = 4001
    CHANNEL_LOGO_UPDATE = 4003
    CHANNEL_LABEL  = 4101
    
    PROGRAM_LABEL    = 4102
    PROGRAM_START    = 3998
    PROGRAM_REMINDER = 3999
    
        
        