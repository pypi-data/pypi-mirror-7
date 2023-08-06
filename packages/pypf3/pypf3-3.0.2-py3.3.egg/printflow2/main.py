'''
Created on Sep 7, 2013

@author: "Colin Manning"
'''
import sys
import getopt
import logging.handlers
import signal

from printflow2.FileSystemMonitor import FileSystemMonitor
from printflow2.NooshMonitor import NooshMonitor

#Global definitions

__printflow2_version__ = "2.5.10"

DJANGO = 'django'

DROPBOX = 'dropbox'
OWNCLOUD = 'owncloud'

fileSystemMonitor = None
nooshMonitor = None
webService = None
framework = None
upload_via = DROPBOX

def close_down(signal, frame):
    print('printflow2 is shutting down')
    if fileSystemMonitor is not None:
        fileSystemMonitor.stop()
    if nooshMonitor is not None:
        nooshMonitor.stop()
    sys.exit(0)

def main():
    global __printflow2_version__
    global fileSystemMonitor
    global nooshMonitor
    global webService
    global framework
    help_text = 'usage:\n printflow2 -c <configfile> -w <workgroup> -l <logfile>  [-f <django>] [-u <owncloud>,<dropbox>]\n printflow2 -v'
    workgroupId = None
    configFile = None
    logFile = None
    logger = None
    framework = None
    try:
        opts, args = getopt.getopt(sys.argv[1:],"vhc:w:l:f:u",["version", "configfile=", "workgroup=","logfile=", "framework=", "upload="])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print(help_text)
            sys.exit()
        elif opt in ("-v", "--version"):
            print(('printflow2 version:',__printflow2_version__))
            sys.exit()
        elif opt in ("-c", "--configfile"):
            configFile = arg
        elif opt in ("-w", "--workgroup"):
            workgroupId = arg
        elif opt in ("-l", "--logfile"):
            logFile = arg
        elif opt in ("-f", "--framework"):
            if arg is DJANGO:
                framework = DJANGO
        elif opt in ("-u", "--upload"):
            if arg is OWNCLOUD:
                upload_via = OWNCLOUD
    
    if configFile is not None and workgroupId is not None:
        # setup logging
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('printflow2')
        handler = logging.handlers.TimedRotatingFileHandler(logFile, when='midnight')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        upload_via = DROPBOX
        
        # disable default logging (INFO level) from 'requests' module

        # Ok, let's go
        # First start listeners in particular the FileSystemMonitor
        # Once NooshMonitor start is called, that's it, as it sits in an infinite loop checking Noosh
        if framework is 'django':
            print(('running printflow2 version:',__printflow2_version__, ' using django framework'))
            fileSystemMonitor = FileSystemMonitor(configFile, workgroupId, upload_via)
            #nooshMonitor = NooshMonitor(configFile, workgroupId, fileSystemMonitor)
            #nooshMonitor = NooshMonitor_django(configFile, workgroupId, fileSystemMonitor, upload_via)
            if fileSystemMonitor.is_ready():
                fileSystemMonitor.scanFolders()
                fileSystemMonitor.start()
                if nooshMonitor.is_ready():
                    nooshMonitor.start()
        else:
            print(('running printflow2 version:',__printflow2_version__, ' using JSON Datastore'))
            fileSystemMonitor = FileSystemMonitor(configFile, workgroupId, upload_via)
            #nooshMonitor = NooshMonitor(configFile, workgroupId, fileSystemMonitor)
            nooshMonitor = NooshMonitor(configFile, workgroupId, fileSystemMonitor, upload_via)
            if fileSystemMonitor.is_ready():
                fileSystemMonitor.scanFolders()
                fileSystemMonitor.start()
                if nooshMonitor.is_ready():
                    nooshMonitor.start()
            
        close_down()
    else:
        print("Invalid call to printflow2")
        print(help_text)
            


signal.signal(signal.SIGINT, close_down)
signal.signal(signal.SIGTERM, close_down)
    
if __name__ == "__main__":
    main()      
