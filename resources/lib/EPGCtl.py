# -*- coding: utf-8 -*-
'''
Handle View positions.
'''
class EPGGridView(object):
    
    '''
    Defining grid view points.
    '''
    def __init__(self):
        self.top = self.left = self.right = self.bottom = self.width = self.cellHeight = 0
        self.start_time = None
        
    
    '''
    Seconds from delta to x position
    '''
    def secondsToX(self, secs):
        return self.left + (secs * self.width / 7200) + 24
        
        

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