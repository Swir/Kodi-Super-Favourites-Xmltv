# -*- coding: utf-8 -*-
import xbmcgui
from os.path import join
from datetime import timedelta, datetime
from threading import Timer
from xbmc import abortRequested
from resources.lib import settings
from resources.lib.utils import strToDatetime
from resources.lib.strings import PROGRAM_NO_INFOS
from resources.lib.superfavourites import ControlSuperFavourites


'''
Handle View positions.
'''

class EPGGridView(object):
    
    window = None
    
    globalGrid = []
    currentGrid = []
    labelControls = []
    superfavs = None
    
    current_x = 0
    current_y = 0
    current_control = None  
    is_closing = False

    
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
        
        desc = self.window.getControl(EPGControl.label.PROGRAM_DESCRIPTION)
        sfx = desc.getWidth() + int(desc.getWidth() / 8.5)
        self.superfavs = ControlSuperFavourites(sfx,desc.getY() + 1 ,400,400, self.focusTexture, self.noFocusTexture)
        
        self.window.addControl(self.superfavs)
        
    
    
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
        self.superfavs.populate()
    
    
    
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
        grid = self.globalGrid[self.start_channel_id : self.start_channel_id + settings.getDisplayChannelsCount()]
        tbr = []
        for channel in grid:
            programs = []
            for program in channel["programs"]:
                
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
                pchannel = xbmcgui.ControlLabel(16, y, 180, self.cellHeight - 2, "[B]" + channel["display_name"] + "[/B]")
            else:
                logo = join(settings.getChannelsLogoPath(), channel["logo"])
                pchannel = xbmcgui.ControlImage(16, y -8, 180, self.cellHeight + 8, logo, aspectRatio=2)
                
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
                                        "stop":  None, "control": pbutton})
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
                                        "stop":  program_end, "control": pbutton})   
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
        
    '''
    Labels reference
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
        
        
        