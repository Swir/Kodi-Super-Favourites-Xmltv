# -*- coding: utf-8 -*-

from os.path import isfile
from xbmc import executebuiltin, log, LOGERROR, abortRequested
from sqlite3 import connect as SqliteConnect, Error as SqliteError
from datetime import datetime as dt
from time import strptime as time_strptime
from threading import Thread, Timer
from datetime import datetime

try:
    from resources.lib.settings import getTablesStructure, getAddonIcon, getEpgDbFilePath, getRemindersTime
    from resources.lib.strings import DIALOG_TITLE, DB_CONNECTION_ERROR, DB_CREATE_TABLES_ERROR, \
                                      DEBUG_HEADER, NOTIFY_PROGRAM_HEADER, NOTIFY_WILL_START_ON

except ImportError:
    from settings import getTablesStructure, getAddonIcon, getEpgDbFilePath, getRemindersTime
    from strings import DIALOG_TITLE, DB_CONNECTION_ERROR, DB_CREATE_TABLES_ERROR, DEBUG_HEADER,\
                        NOTIFY_PROGRAM_HEADER, NOTIFY_WILL_START_ON
    
import xbmc

'''
Display a basic notification
'''    

def notify(message, plus=None):
    message = message.encode("utf-8", 'ignore')
    log(message, LOGERROR)
    if not plus is None:
        log(plus, LOGERROR)
        
    executebuiltin('Notification(%s,%s,%s,%s)'%(DIALOG_TITLE.encode("utf-8", 'ignore'), message, 6000, getAddonIcon()))
    
    
    
'''
Return a datetim from string as %Y%m%d%H%M%S
'''
def strToDatetime(datestr):
    try:
        return dt.strptime(datestr, "%Y%m%d%H%M%S")
    except TypeError:
        return dt(*(time_strptime(datestr, "%Y%m%d%H%M%S")[0:6]))
    
    
    
'''
Database connection.
    '''
def connectEpgDB():
    
    def connect():
        try:
            database = SqliteConnect(getEpgDbFilePath())
            database.text_factory = str
            cursor = database.cursor()
        except SqliteError as e:
            notify(DB_CONNECTION_ERROR, e.message)
            return None
        
        return database, cursor
    
    
    if not isfile(getEpgDbFilePath()):
        database, cursor = connect()
        if database is None:
            return None, None
        
        channels_str, programs_str, updates, notifications = getTablesStructure()      
        update_flag  = "INSERT INTO updates (time) VALUES ('-1')"
        
        try:
            cursor.execute(channels_str)
            cursor.execute(programs_str)
            cursor.execute(updates)
            cursor.execute(update_flag)
            cursor.execute(notifications)
            database.commit()
            
        except SqliteError as e:
            notify(DB_CREATE_TABLES_ERROR, e.message)
            return None, None
        return database, cursor

    else:
        return connect()
    
    

'''
Copy a file from source to dest.
'''
def copyfile(source, dest, buffer_size=1024*1024):
    
    source = open(source, "rb")
    destin = open(dest, "wb")
    
    while 1:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        destin.write(copy_buffer)
        
        

'''
Handle the threaded programs notifier.
'''
class ThreadedNotifier(Thread):
    
    database = cursor = None
    epgDb = None
   
    '''
    Init
    '''
    def __init__(self):
        Thread.__init__(self)
        
    
    '''
    Thread run
    '''
    def run(self):
        try:
            xbmc.sleep(2000)
            self.startNotifier()
        except Exception as e:
            log("%s %s" % ( DEBUG_HEADER, e.message), LOGERROR)
    
    
    '''
    Start notifier
    '''
    def startNotifier(self, timer=True):
        self.database, self.cursor = connectEpgDB()
        
        programs = self.getProgramsToBeNotified()
        delta = getRemindersTime()
        header = NOTIFY_PROGRAM_HEADER.encode("utf-8", "ignore")
        
        for program in programs:            
            if strToDatetime(program["start"]) + delta >= datetime.now() :
                if strToDatetime(program["start"]) <= datetime.now() + delta:
                    # Then notify it and delete record
                    message = program["title"] + " " + NOTIFY_WILL_START_ON + " " + program["channel"]
                    self.removeReminder(program["id_program"])
                    xbmc.executebuiltin("Notification(" + header + "," + message.encode("utf-8", "ignore") + ", 8000, " + getAddonIcon() + ")")
                    xbmc.sleep(12000)
                
        if timer:
            Timer(60, self.startNotifier, {timer: not abortRequested}).start()
    
    
    '''
    Return the current programs that are to be notified
    '''
    def getProgramsToBeNotified(self):
        reminders = []
        request ="SELECT * FROM reminders"
        self.cursor.execute(request)
        request = self.cursor.fetchall()
        
        for ids in request:
            check = "SELECT count(*) FROM programs WHERE id_program=%i" % ids[1]
            self.cursor.execute(check)
            exists = True if int(self.cursor.fetchone()[0]) > 0 else False
            
            if not exists:
                self.removeReminder(ids[1])
            else:
                psearch = "SELECT start_date, title, channel FROM programs WHERE id_program=%i" % ids[1]  
                self.cursor.execute(psearch)
                result = self.cursor.fetchone()
            
                start_date = result[0]
                title = result[1].decode("utf-8", 'ignore')
                channel = result[2].decode("utf-8", 'ignore')
            
                if strToDatetime(start_date) < datetime.now():
                    self.removeReminder(ids[1])
                else:
                    check = 'SELECT count(*) FROM channels WHERE id_channel="%s"' % channel
                    self.cursor.execute(check)
                    exists = True if int(self.cursor.fetchone()[0]) > 0 else False
                    
                    if exists:
                        chan = 'SELECT display_name FROM channels WHERE id_channel="%s"' % channel
                        self.cursor.execute(chan)
                        channel = self.cursor.fetchone()[0]
                        reminders.append({"id_program":ids[1], "channel":channel, "title":title, "start":start_date})
                    else:
                        self.removeReminder(ids[1])
        return reminders
    
    
    
    '''
    Delete a reminder
    '''
    def removeReminder(self, id_program):
        delete = "DELETE FROM reminders WHERE id_program=%i" % id_program
        self.cursor.execute(delete)
        self.database.commit()
        
    