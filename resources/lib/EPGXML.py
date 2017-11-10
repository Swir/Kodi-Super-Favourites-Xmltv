import os
import sqlite3

from resources.lib import utils

'''
Handle SQL EPG guide
'''
class EpgDb(object):
    
    DEBUG = False
    
    database = None
    cursor = None
    addon    = None
    db_path  = None 
    init_result = False
    
    '''
    EPG DB init.
    '''
    def __init__(self, addon_obj, debug=False):
        self.addon = addon_obj
        self.DEBUG = debug
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
            self.cursor = self.database.cursor()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33401, e.message)
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
        programs_str = "CREATE TABLE programs(id_program INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT)"
                
        try:
            self.cursor.execute(channels_str)
            self.cursor.execute(programs_str)
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33402, e.mesage)
            self.database = None
            return False
        return True
    
    
    '''
    Return the initialization state.
    '''
    def isDBInitOk(self):
        return self.init_result
    
    
    '''
    Add a channel definition into the database.
    '''
    def addChannel(self, cid, display_name, logo='', source='', visible=True):
        try:
            if visible:
                visible = '1'
            else:
                visible = '0'
            channel = "INSERT INTO channels (id, display_name, logo, source, visible) "
            values  = 'VALUES ("%s","%s","%s","%s",%s)' % (cid,display_name,logo,source,visible)
        
            self.cursor.execute(channel + values)
            self.database.commit()
        
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33403, e.message)
            return False
        
        return True
    
    
    '''
    Update a given channel.
    '''
    def updateChannel(self, id_channel, cid_channel=None, display_name=None, logo=None, source=None, visible=None):
        
        try:
            update = "UPDATE channels set "
            
            if not cid_channel is None:
                update += 'id="%s",' % (cid_channel, )
                # Updating programs
                programs = 'UPDATE programs SET channel="%s" WHERE id="%s"' % (cid_channel, id_channel)
                self.cursor.execute(programs)
                self.database.commit()
            
            if not display_name is None:
                update += 'display_name="%s",' % (display_name, )
            
            if not logo is None:
                update += 'logo="%s",' % (logo, )
             
            if not source is None:   
                update += 'source="%s",' % (source, )
            
            if not visible is None:
                update += 'visible=%i' % (1 if visible else 0, )
            
            update += ' WHERE id="%s"' % (id_channel,)
            if visible is None:
                update = ''.join(update.rsplit(",", 1))

            self.cursor.execute(update) 
            self.database.commit()
            
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33404, e.message)
            return False
        
        return True
    
    
    '''
    Remove a channel.
    '''
    def removeChannel(self, id_channel):
        try:
            # Channel
            delete = 'DELETE FROM channels WHERE id="%s"' % (id_channel, )
            # Programs
            programs = 'DELETE FROM programs WHERE channel="%s"' % (id_channel, )
            self.cursor.execute(delete)
            self.cursor.execute(programs)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33405, e.message)
            return False
        
        return True
    
    
    '''
    Return the asked channel
    '''
    def getChannel(self, id_channel):
        try:
            get = 'SELECT * FROM channels WHERE id="%s"' % (id_channel, )
            self.cursor.execute(get)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33406, e.message)
            return False
        
        return False
    
    
    
    '''
    Add a program into the program table.
    '''
    def addProgram(self, channel, title, start_date, end_date, description):
        try:
            program = "INSERT INTO programs (channel, title, start_date, end_date, description) "
            values  = 'VALUES ("%s","%s",%i,%i,"%s")' % (channel,title,start_date,end_date,description)
            self.cursor.execute(program + values)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33407, e.message)
            return False
        return True
    
    
    '''
    Update a program into the tale.
    '''
    def updateProgram(self, id_program, channel=None, title=None, start_date=None, end_date=None, description=None):
        try:
            update = "UPDATE programs set "
            
            if not channel is None:
                update += 'channel="%s",' % channel
            
            if not title is None:
                update += 'title="%s",' % title
             
            if not start_date is None:   
                update += 'start_date=%i,' % start_date
            
            if not end_date is None:
                update += 'end_date=%i,' % end_date
            
            if not description is None:
                update += 'description="%s" ,' % description
            
            update += ' WHERE id_program=%i' % (id_program,)
            update = ''.join(update.rsplit(",", 1))

            self.cursor.execute(update) 
            self.database.commit()
            
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33410, e.message)
            return False
        
        return True
    
    
    
    '''
    Remove a program from the program tale.
    '''
    def removeProgram(self, id_channel, id_program):
        try:
            program = 'DELETE FROM programs WHERE channel="%s" AND id_program=%i' % (id_channel, id_program)
            self.cursor.execute(program)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33408, e.message)
            return False
        
        return True
    
    
    '''
    Return asked program.
    '''
    def getProgram(self, id_channel, id_program):
        try:
            get = 'SELECT * FROM programs WHERE channel="%s" AND id_program=%i' % (id_channel, id_program)
            self.cursor.execute(get)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33409, e.message)
            return False
        
        return False
    
    
    '''
    Return all available channels
    '''
    def getAllChannels(self):
        try:
            get = 'SELECT * FROM channels WHERE 1'
            self.cursor.execute(get)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33412, e.message)
            return False
        
        return False
    
    
    
    '''
    Return all programs for a given channel
    ''' 
    def getChannelPrograms(self, id_channel):
        try:
            get = 'SELECT * FROM programs WHERE channel="%s"' % id_channel
            self.cursor.execute(get)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            if self.DEBUG:
                utils.notify(self.addon, 33413, e.message)
            return False
        
        return False
    
    
    '''
    Return True if the given channel has programs into the db.
    '''
    def hasPrograms(self, id_channel):
        return len(self.getChannelPrograms(id_channel)) > 0
    
    
    '''
    Truncate the programs table
    '''
    def truncatePrograms(self):
        return self.__truncate('programs', 33414)
    
    
    '''
    Truncate the channels table
    '''
    def truncateChannels(self):
        return self.__truncate('channels', 33415)
    
    
    '''
    Clean both channels and programs
    '''
    def getCleanAll(self):
        a = self.truncateChannels()
        b = self.truncatePrograms()
        return a and b
    
    
    '''
    Delete all passed programs
    '''
    def getCleanOld(self):
        #33416
        pass
    
    
    '''
    Global truncate
    '''
    def __truncate(self, table, error=None):
        try:
            request = "DELETE FROM %s" % table
            self.cursor.execute(request)
            self.database.commit()
        except sqlite3.Error as err:
            if self.DEBUG and not error is None:
                utils.notify(self.addon, 33414, err.message)
            return False
        return True
        
        