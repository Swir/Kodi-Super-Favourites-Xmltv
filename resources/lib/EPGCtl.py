# -*- coding: utf-8 -*-
from os.path import join
from resources.lib.settings import getTimelineToDisplay, getDisplayChannelsCount, getAddonImagesPath
from resources.lib.utils import strToDatetime
from resources.lib.strings import PROGRAM_NO_INFOS
import xbmcgui, xbmc
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
    
    '''
    Defining grid view points.
    '''
    def __init__(self, window):
        self.window = window
        self.top = self.left = self.right = self.bottom = self.width = self.cellHeight = 0
        self.start_time = self.stop_time = None
        self.start_channel_id = 0
        
        self.noFocusTexture = join(getAddonImagesPath(), 'buttons', 'tvguide-program-grey.png')
        self.focusTexture = join(getAddonImagesPath(), 'buttons', 'tvguide-program-grey-focus.png')
    
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
        epgbtn = self.currentGrid[y][x]
        self.window.setFocus(epgbtn["control"]) 
    
    
    
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
        return self.left + (secs * self.width / (getTimelineToDisplay() * 60)) + 24
     
     
     
    '''                              '''
    ''' Grid Data from EPGdb related '''
    ''' _____________________________'''  
           
        
    '''
    Return channels count
    '''
    def getChannelsCount(self):
        return len(self.globalGrid)
        
    
    '''
    Return a grid portion based on channels count and programs time
    '''
    def __getGridPortion(self):
        grid = self.globalGrid[self.start_channel_id : self.start_channel_id + getDisplayChannelsCount()]
        tbr = []
        for channel in grid:
            programs = []
            for program in channel["programs"]:
                
                stop = strToDatetime(program["end"])
                start = strToDatetime(program["start"])
                
                if stop > self.start_time and start < self.stop_time:
                    programs.append(program)
            
            tbr.append({"db_id":channel["db_id"],"id_channel": channel["id_channel"], 
                         "display_name" : channel["display_name"], "programs": programs
                        }) 
        return tbr
    
        
    
    '''                              '''
    '''     Grid user manipulation   '''
    ''' _____________________________''' 
    
    '''
    Sets channels lines
    '''
    def setChannels(self):
        self.reset(clear_grid=True)
        EPG_page = self.__getGridPortion() 
        
        gridControls = []
        idx = 0
        for channel in EPG_page:            
            y = self.top + self.cellHeight * idx + int((self.cellHeight / 14))
            pchannel = xbmcgui.ControlLabel(16, y, 180, self.cellHeight - 2, "[B]" + channel["display_name"] + "[/B]")
            
            self.window.addControl(pchannel)
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
        
        
    
    def next(self):
        if len(self.currentGrid[self.current_y]) - 1 == self.current_x:
            return False
        else:
            self.current_x += 1
            self.setFocus(self.current_x, self.current_y)
    
    
    def previous(self):
        if self.current_x == 0:
            return False
        else:
            self.current_x -= 1
            self.setFocus(self.current_x, self.current_y)
    
    
    def up(self):
        if self.current_y == 0:
            return False
        else:
            self.current_y -= 1
            self.current_x = 0
            self.setFocus(self.current_x, self.current_y)
    
    
    def down(self):
        #xbmc.log(str(len(self.currentGrid)), xbmc.LOGERROR)
        if len(self.currentGrid) - 1 == self.current_y:
            return False
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
        
        
        