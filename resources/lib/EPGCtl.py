# -*- coding: utf-8 -*-
from resources.lib.settings import getTimelineToDisplay, getDisplayChannelsCount
import xbmcgui, xbmc
'''
Handle View positions.
'''
from resources.lib.utils import strToDatetime

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
    
    '''
    Sets grid as a list of controls
    y_grid as a list
    '''
    def append(self, y_grid):
        self.currentGrid.append(y_grid)
        self.reset()
        self.setFocus(self.current_x, self.current_y)
        
    
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
        for y in self.currentGrid:
            for x in y:
                self.window.removeControl(self.window.getControl(x["control_id"]))
        del self.currentGrid[:]
        self.currentGrid = []
        
        for i in self.labelControls:
            self.window.removeControl(i)
        del self.labelControls[:]
        self.labelControls = []
        
        
    '''
    Return channels count
    '''
    def getChannelsCount(self):
        return len(self.globalGrid)
        
    
    '''
    Return a grid portion based on channels count and programs time
    '''
    def getGridPortion(self):
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
    
    
    '''
    Set the focus to the given control coordonates.
    '''
    def setFocus(self, x, y):
        epgbtn = self.currentGrid[y][x]
        self.current_control = epgbtn["control_id"]
        self.window.setFocusId(self.current_control) 
        
    
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
                if x["control_id"] == controlID:
                    return x, cy, y.index(x)
        return None, self.current_y, self.current_x
    
    
    '''
    Return True if the given control ID is a program control ID
    '''
    def isProgramControl(self, controlID):
        status, y, x = self.getInfosFromCurrentGrid(controlID)
        return status is not None
    
    
    
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
    Seconds from delta to x position
    '''
    def secondsToX(self, secs):
        return self.left + (secs * self.width / (getTimelineToDisplay() * 60)) + 24



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
        
        
        