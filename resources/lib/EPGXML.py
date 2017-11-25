# -*- coding: utf-8 -*-

import os, time, glob, shutil
import datetime
import sqlite3
import urllib2
import zipfile, tarfile
import xbmcgui

from xml.dom import minidom
from resources.lib.utils import notify, copyfile
from resources.lib import strings, settings

'''
Handle XMLTV itself.
'''
class EpgXml(object):
    
    DEBUG = False
    
    XMLTV_SOURCE_URL   = 0
    XMLTV_SOURCE_LOCAL = 1
    
    addon    = None
    epg_db   = None
    database = None
    cursor   = None
    
    xmltv_file   = None
    xmltv_source = 0
    xmltv_global_path = None
    xmltv_progress_bar = None
    
        
    def __init__(self, progress_bar=True):
        self.DEBUG = False
        self.addon = settings.addon
        
        self.epg_db = EpgDb()
        
        self.xmltv_source = int(self.addon.getSetting("xmltv.source.type"))
        
        self.xmltv_global_path = self.addon.getAddonInfo('path')
        self.xmltv_global_path = self.xmltv_global_path.replace('addons', os.path.join('userdata', 'addon_data'), 1)       
     
        if progress_bar:
            self.xmltv_progress_bar = xbmcgui.DialogProgress()
        else:
            self.xmltv_progress_bar = xbmcgui.DialogProgressBG()        
            
    
           
     
    '''
    Set the database object ( multi threading purpose )
    '''
    def setDatabaseObj(self, db):
        self.database = db
        self.init_result = True if not self.database is None else False
    
    
    
    '''
    Set the cursor object ( multi threading purpose )
    '''
    def setCursorObj(self, cursor):
        self.cursor = cursor   
    
    
    
    '''
    Global entry point to get / parse and push xmltv data into db.
    '''
    def getXMLTV(self):
        
        if self.database is None or self.cursor is None:
            return
        
        self.epg_db.setCursorObj(self.cursor)
        self.epg_db.setDatabaseObj(self.database)
            
        if os.path.isfile(os.path.join(self.xmltv_global_path, "epg.xml")):
            os.remove(os.path.join(self.xmltv_global_path, "epg.xml")) 
                
        if  self.xmltv_source == EpgXml.XMLTV_SOURCE_LOCAL:
            self.xmltv_file = self.__getLocalXmltv(self.addon.getSetting('xmltv.local.value'))
        
        elif self.xmltv_source == EpgXml.XMLTV_SOURCE_URL:
            self.xmltv_file = self.__getUrlXmltv(self.addon.getSetting('xmltv.url.value'))
        
        else:
            notify(strings.XMLTV_LOAD_ERROR)
        
        
        
        if not self.xmltv_file is None:
            # parsing xmltv file
            self.__parseXMLTV(self.xmltv_file)
            
    
    '''
    Basic xml file checks
    '''
    def __getLocalXmltv(self, local_file):
                
        compressed = True if self.addon.getSetting('xmltv.compressed') == 'true' else False 
        
        if not os.path.isfile(local_file):
            notify(strings.XMLTV_FILE_NOT_FOUND)
        else:
            if not compressed and not local_file.endswith(".xml"):
                notify(strings.BAD_XMLTV_FILE_TYPE)
                return None
            elif not compressed:
                # Moving to userdata
                if not self.xmltv_source == EpgXml.XMLTV_SOURCE_URL:
                    copyfile(local_file, os.path.join(self.xmltv_global_path, "epg.xml"))
                
                local_file = os.path.join(self.xmltv_global_path, "epg.xml")
                return local_file
            else:
                # Uncompress and moving to userdata
                return self.__uncompressAndMove(local_file)
        
        
    
    
    '''
    Retrive an xmltv file from a given url.
    '''
    def __getUrlXmltv(self, url_file_source):
        
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        dest_file = os.path.join(self.xmltv_global_path, "epg.xml")        
        
        try:
            self.xmltv_progress_bar.create(strings.SFX_EPG_UPDATE_HEADER, strings.SFX_DOWNLOADING_MSG)
            download = urllib2.urlopen(url_file_source, timeout=30)
            
            # Most of tried servers are data chunked ( no content length header ) so faking progress
            self.xmltv_progress_bar.update(25)
                        
        except urllib2.HTTPError as e:
            if e.code == 304:
                notify(strings.HTTP_UNCHANGED_REMOTE_FILE, e.reason)  
            elif e.code == 301:    
                notify(strings.HTTP_MOVED_PERMANENTLY, e.reason)
            elif e.code == 400:
                notify(strings.HTTP_BAD_REQUEST, e.reason)
            elif e.code == 401:
                notify(strings.HTTP_UNAUTHORIZED, e.reason)   
            elif e.code == 403:
                notify(strings.HTTP_UNAUTHORIZED, e.reason)    
            elif e.code == 404:
                notify(strings.HTTP_NOT_FOUND, e.reason)
            elif e.code == 500:
                notify(strings.HTTP_INTERNAL_SERVER_ERROR, e.reason)
            elif e.code == 502:
                notify(strings.HTTP_BAD_GATEWAY, e.reason)
            elif e.code == 503:
                notify(strings.HTTP_SERVER_OVERLOADED, e.reason)
            elif e.code == 504:
                notify(strings.HTTP_REQUEST_TIMEOUT, e.reason)
            else:
                notify(strings.HTTP_UNHANDLED_ERROR, e.reason)
            
            self.xmltv_progress_bar.close()
               
            return None
        
        if os.path.isfile(dest_file):
            os.remove(dest_file)
        
        self.xmltv_progress_bar.update(35)
        tsf = open(dest_file, "w")
        self.xmltv_progress_bar.update(60)
        tsf.write(download.read())
        self.xmltv_progress_bar.update(8)
        tsf.close()
        self.xmltv_progress_bar.update(100)

        del tsf
        self.xmltv_progress_bar.close()
        
        return self.__getLocalXmltv(dest_file)
    


    '''
    Uncompress zip, tar, ... archive and moves it into the right directory.
    '''
    def __uncompressAndMove(self, zfile):
        
        dest = os.path.join(self.xmltv_global_path, "epg.archive")                
        
        if zipfile.is_zipfile(zfile):
            try:
                with zipfile.ZipFile(zfile, "r") as xmltv_zip:
                    xmltv_zip.extractall(dest)
                    xmltv_zip.close()
                    
            except zipfile.BadZipfile, zipfile.LargeZipFile:
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                notify(strings.ARCHIVE_ZIP_UNCOMPRESS_ERROR)
                return None
            
        elif tarfile.is_tarfile(zfile):
                try:
                    with tarfile.TarFile(zfile) as xmltv_tar:
                        xmltv_tar.extractall(dest)
                        xmltv_tar.close()
                        
                except tarfile.ReadError:
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    notify(strings.ARCHIVE_TAR_UNCOMPRESS_ERROR)
                    return None
        else:
            notify(strings.ARCHIVE_UNSUPPORTED_FORMAT)
            return None
        
        if os.path.isdir(dest):
            paths = glob.glob(os.path.join(dest, "*.xml"))
            if len(paths) <= 0:
                notify(strings.ARCHIVE_NO_XMLTV_FOUND)
                shutil.rmtree(dest)
                return None
            else:
                zfile = None
                for ptest in paths:
                    xmltest = minidom.parse(ptest) 
                    
                    channels = True if xmltest.getElementsByTagName('channel').length > 0 else False
                    programs = True if xmltest.getElementsByTagName('programme').length > 0 else False
                    
                    if channels and programs:
                        os.rename(ptest, os.path.join(self.xmltv_global_path, "epg.xml"))
                        shutil.rmtree(dest)
                        zfile = os.path.join(self.xmltv_global_path, "epg.xml")
                        break
        else:
            notify(strings.ARCHIVE_UNSUPPORTED_FORMAT)
            return None
        
        return zfile
    
    
    
    '''
    Parse the xmltv file and return the result.
    '''
    def __parseXMLTV(self, xmltv):
        self.xmltv_progress_bar.create(strings.DIALOG_TITLE, strings.SFX_LONG_TIME_MSG)
        xmltv = minidom.parse(xmltv)
        channels = xmltv.getElementsByTagName('channel')
        programs = xmltv.getElementsByTagName('programme')
        plist = []
        clist = []

        i = 1
        for channel in channels:
            
            percent = int( ( i / float(channels.length) ) * 100)
            message = strings.SFX_CHANNEL + ' %i/%i' % (i, channels.length)
            self.xmltv_progress_bar.update(percent, "", message)
            
            id_channel   = channel.getAttribute('id').encode('utf-8', 'ignore') 
            display_name = channel.getElementsByTagName('display-name')[0].firstChild.data.encode('utf-8', 'ignore')
            display_name = display_name.replace(r'/', '-')
            display_name = display_name.replace("\\", "-")
            
            if not self.epg_db.channelExists(id_channel):
                clist.append([id_channel, display_name, '', '', '1'])
            i += 1
        
        self.epg_db.addChannels(clist)
           
        
        self.epg_db.truncatePrograms()
        i = 1
        for program in programs:
            
            percent = int( ( i / float(programs.length) ) * 100)
            message = strings.SFX_PROGRAM + ' %i/%i' % (i, programs.length)
            self.xmltv_progress_bar.update(percent, "", message)
            
            id_channel = program.getAttribute('channel') .encode('utf-8', 'ignore')           
            
            start_date = program.getAttribute('start')
            start_date = start_date.encode('utf-8', 'ignore')
            
            if start_date.find(' +'):
                start_date = start_date[:start_date.find(" +")]             
              
            end_date = program.getAttribute('stop')
            end_date = end_date.encode('utf-8', 'ignore')
            if end_date.find(' +'):
                end_date = end_date[:end_date.find(" +")] 
            
            try:
                program_start = datetime.datetime.strptime(start_date, "%Y%m%d%H%M%S")
                program_end = datetime.datetime.strptime(end_date, "%Y%m%d%H%M%S")
            except TypeError:
                program_start = datetime.datetime(*(time.strptime(start_date, "%Y%m%d%H%M%S")[0:6]))
                program_end = datetime.datetime(*(time.strptime(end_date, "%Y%m%d%H%M%S")[0:6]))
            
            ptitle = ""
            if program.getElementsByTagName('title').length > 0:
                try:
                    ptitle = program.getElementsByTagName('title')[0].firstChild.data
                    ptitle = ptitle.encode('utf-8', 'ignore')
                except AttributeError:
                    ptitle = ""
            
            desc = ""
            if program.getElementsByTagName('desc').length > 0:
                try:
                    desc = program.getElementsByTagName('desc')[0].firstChild.data
                    desc = desc.encode('utf-8', 'ignore')
                except AttributeError:
                    desc = ""
            
            if program_end > datetime.datetime.now():
                plist.append([id_channel, ptitle, program_start.strftime("%Y%m%d%H%M%S"), program_end.strftime("%Y%m%d%H%M%S"), desc])
            
            i += 1
            
        self.epg_db.addPrograms(plist)
        
        self.xmltv_progress_bar.close()

            
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
    def __init__(self):
        self.addon = settings.addon
        self.DEBUG = False
        #base = os.path.dirname(os.path.realpath(__file__))
        
        base = self.addon.getAddonInfo('path')
        base = base.replace('addons', os.path.join('userdata', 'addon_data'), 1)
        self.db_path = os.path.join(base, "epg.db")
            
    
    '''
    Set the database object ( multi threading purpose )
    '''
    def setDatabaseObj(self, db):
        self.database = db
        self.init_result = True if not self.database is None else False
    
    
    '''
    Set the cursor object ( multi threading purpose )
    '''
    def setCursorObj(self, cursor):
        self.cursor = cursor
                 
    
    '''
    Return the initialization state.
    '''
    def isDBInitOk(self):
        return self.init_result
    
    
    '''
    Add a channel definition into the database.
    '''
    def addChannels(self, clist):
        try:
            for channel in clist:
                chann = "INSERT INTO channels (id_channel, display_name, logo, source, visible) VALUES (?,?,?,?,?)"
                self.cursor.execute(chann, (channel[0],channel[1],channel[2],channel[3],channel[4]))
                
            self.database.commit()
        
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.ADDING_CHANNEL_ERROR, e.message)
            return False
        
        return True
    
    
    '''
    Update a given channel.
    '''
    def updateChannel(self, id_channel, cid_channel=None, display_name=None, logo=None, source=None, visible=None):
        
        try:
            update = "UPDATE channels set "
            
            if not cid_channel is None:
                update += 'id_channel="%s",' % (cid_channel, )
                # Updating programs
                programs = 'UPDATE programs SET channel="%s" WHERE id_channel="%s"' % (cid_channel, id_channel)
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
            
            update += ' WHERE id_channel="%s"' % (id_channel,)
            if visible is None:
                update = ''.join(update.rsplit(",", 1))

            self.cursor.execute(update) 
            self.database.commit()
            
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.UPDATE_CHANNEL_ERROR, e.message)
            return False
        
        return True
    
    
    '''
    Remove a channel.
    '''
    def removeChannel(self, id_channel):
        try:
            # Channel
            delete = 'DELETE FROM channels WHERE id_channel="%s"' % id_channel
            # Programs
            programs = 'DELETE FROM programs WHERE channel="%s"' % id_channel
            self.cursor.execute(delete)
            self.cursor.execute(programs)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.REMOVE_CHANNEL_ERROR, e.message)
            return False
        
        return True
    
    
    '''
    Return the asked channel
    '''
    def getChannel(self, id_channel):
        try:
            get = 'SELECT * FROM channels WHERE id_channel="%s"' % id_channel
            self.cursor.execute(get)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.GET_CHANNEL_ERROR, e.message)
            return False
        
        return False
    
    
    '''
    Return True if channel exists.
    '''
    def channelExists(self, id_channel):
        try:
            check = 'SELECT count(*) as count FROM channels WHERE id_channel="%s"' % id_channel
            self.cursor.execute(check)
            return self.cursor.fetchone()[0] == 1
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.GET_CHANNEL_ERROR, e.message)
    
    '''
    Add a program into the program table.
    '''
    def addPrograms(self, program_list):
        
        try:
            for program in program_list:
                program_req = 'INSERT INTO programs (channel, title, start_date, end_date, description) VALUES (?,?,?,?,?)'            
                self.cursor.execute(program_req, (program[0], program[1], program[2], program[3], program[4]))
            
            self.database.commit()
            
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.ADDING_PROGRAM_ERROR, e.message)
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
                update += 'start_date="%s",' % start_date
            
            if not end_date is None:
                update += 'end_date="%s",' % end_date
            
            if not description is None:
                update += 'description="%s" ,' % description
            
            update += ' WHERE id_program=%i' % (id_program,)
            update = ''.join(update.rsplit(",", 1))

            self.cursor.execute(update) 
            self.database.commit()
            
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.UPDATE_PROGRAM_ERROR, e.message)
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
                notify(strings.REMOVE_PROGRAM_ERROR, e.message)
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
                notify(strings.GET_PROGRAM_ERROR, e.message)
            return False
        
        return False
       
    
    '''
    Return all programs for a given channel
    ''' 
    def getChannelPrograms(self, id_channel, start_time, end_time):
        try:            
            between_v1 = start_time.strftime("%Y%m%d%H%M%S")
            between_v2 = end_time.strftime("%Y%m%d%H%M%S")
            get = 'SELECT * FROM programs WHERE channel="%s" AND ((CAST(end_date AS INTEGER) BETWEEN %i AND %i) OR (CAST(start_date AS INTEGER) BETWEEN %i AND %i)) ORDER BY start_date ASC' % (id_channel, int(between_v1), int(between_v2), int(between_v1), int(between_v2))
            self.cursor.execute(get)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.GET_CHANNEL_PROGRAMS_ERROR, e.message)
            return False
        
        return False
    
    
    
    '''
    Return all available channels
    '''
    def getAllChannels(self, channels_limit=9):
        try:
            get = 'SELECT * FROM channels WHERE visible="1" ORDER BY id ASC LIMIT %i' % channels_limit
            self.cursor.execute(get)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.GET_CHANNELS_ERROR, e.message)
            return False
        
        return False
    
    
    
    '''
    Return the complete EPG grid.
    '''
    def getEpgGrid(self, start_dt, end_dt, limit=9):
        
        channels = self.getAllChannels(channels_limit=limit)
        
        grid = dict()
                             
        for channel in channels:
            programs = self.getChannelPrograms(channel[1], start_dt, end_dt)
            
            programs_list = []
            for program in programs:
                # Storing program
                plist = {"title": program[2], "desc": program[5], "start": program[3], "end": program[4]}
                programs_list.append(plist)    
                                
            grid[channel[0]] = {"id_channel": channel[1], "display_name" : channel[2], "programs": programs_list}
        
        return grid
    
    
    '''
    Return True if the given channel has programs into the db.
    '''
    def hasPrograms(self, id_channel):
        return len(self.getChannelPrograms(id_channel)) > 0
    
    
    '''
    Truncate the programs table
    '''
    def truncatePrograms(self):
        return self.__truncate('programs', strings.DB_PROGRAMS_TRUNCATE_ERROR)
    
    
    '''
    Truncate the channels table
    '''
    def truncateChannels(self):
        return self.__truncate('channels', strings.DB_CHANNELS_TRUNCATE_ERROR)
    
    
    '''
    Clean both channels and programs
    '''
    def getCleanAll(self):
        a = self.truncateChannels()
        b = self.truncatePrograms()
        return a and b
    
    
    '''
    Return True if this is the FIRST launch or eĝ.db ad epg.xml were deleted.
    '''
    def firstTimeRuning(self):
        if self.cursor is None or self.database is None:
            return
        try:
            check = "SELECT COUNT(*) as count FROM updates WHERE time='-1'"
            self.cursor.execute(check)
            return int(self.cursor.fetchone()[0]) == 1 
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.DB_STATE_ERROR, e.message)
            return False
    
    
    '''
    Set the first time start flag..
    '''
    def setFirstTimeRuning(self, state):
        if self.cursor is None or self.database is None:
            return
        try:
            check = "UPDATE updates set time ='%s' WHERE id_update=1" % state
            self.cursor.execute(check)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.DB_STATE_ERROR, e.message)    
    
    '''
    Delete all passed programs
    '''
    def getCleanOld(self): 
        programs = "SELECT id_program, end_date FROM programs"
        try:
            if self.cursor is None or self.database is None:
                return
            
            self.cursor.execute(programs)
            
            for program in self.cursor.fetchall():
                    
                program_end_date = program[1]
                    
                treshold = self.addon.getSetting('cleanup.treshold')
                if treshold is None or treshold == '':
                    treshold = '1'
                    
                current_time = datetime.datetime.fromtimestamp(time.time())
                try:
                    program_time = datetime.datetime.strptime(program_end_date, "%Y%m%d%H%M%S")
                except TypeError:
                    program_time = datetime.datetime(*(time.strptime(program_end_date, "%Y%m%d%H%M%S")[0:6]))
                    
                delta = current_time - program_time
                    
                if delta.days >= int(treshold) + 1 :
                    # Then delete old ones.
                    request = "DELETE FROM programs WHERE id_program=%i" % program[0]
                    self.cursor.execute(request)
                    self.database.commit()
                
        except sqlite3.Error as e:
            if self.DEBUG :
                notify(strings.CLEANUP_PROGRAMS_ERROR, e.message)
                
                
    '''
    '''
    def getLastUpdateDate(self):
        if self.cursor is None or self.database is None:
            return
        try:
            check = "SELECT time FROM updates WHERE 1 ORDER BY id_update DESC LIMIT 1"
            self.cursor.execute(check)
            res = self.cursor.fetchone()[0]
            if res in (-1, 0):
                return None
            return str(res)
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.LAST_UPDATE_NOT_FOUND, e.message)   
    
    
    '''
    '''
    def setUpdateDate(self):
        if self.cursor is None or self.database is None:
            return
        try:
            dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')            
            date_insert = "INSERT INTO updates (time) VALUES ('%s')" % dt
            self.cursor.execute(date_insert)
            self.database.commit()
        except sqlite3.Error as e:
            if self.DEBUG:
                notify(strings.REGISTER_UPDATE_ERROR, e.message)   
                
    
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
                notify(error, err.message)
            return False
        return True
    
    
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
        
        