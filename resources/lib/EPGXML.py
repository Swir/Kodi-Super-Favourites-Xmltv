import os
import sqlite3

from resources.lib import utils

'''
Handle SQL EPG guide
'''
class EpgDb(object):
    
    
    database = None
    addon    = None
    db_path  = None 
    init_result = False
    
    '''
    EPG DB init.
    '''
    def __init__(self, addon_obj):
        self.addon = addon_obj
        #base = os.path.dirname(os.path.realpath(__file__))
        
        base = self.addon.getAddonInfo('path')
        base = base.replace('addons', os.path.join('userdata', 'addon_data'), 1)
        self.db_path = base + "/epg.db"
        
        if not os.path.isfile(self.db_path):
            # This is a fresh install or a hard reset ,
            self.init_result = self.create_db()
        else:
            self.init_result = self.connect()

    
    '''
    Database connection.
    '''
    def connect(self):
        try:
            self.database = sqlite3.connect(self.db_path)
        except sqlite3.Error:
            utils.notify(self.addon, 33401)
            self.database = None
            return False
        
        return True
        
            
            
    ''' 
    Create the global DB structure.
    '''
    def create_db(self):
        
        self.connect()
        if self.database is None:
            return False
        
        channels_str = "CREATE TABLE channels (id TEXT, display_name TEXT, logo TEXT, source TEXT, visible BOOLEAN, PRIMARY KEY (id))"
        programs_str = "CREATE TABLE programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT)"
        
        cursor = self.database.cursor()
        
        try:
            cursor.execute(channels_str)
            cursor.execute(programs_str)
        except sqlite3.Error:
            utils.notify(self.addon, 33402)
            self.database = None
            return False
        return True
    
    
    '''
    Return the initialization state.
    '''
    def isDBInitOk(self):
        return self.init_result
    
    