from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from collections import namedtuple

ClientData=namedtuple('ClientData','name IP port')

class Server(DirectObject):
    def __init__(self):
        log.debug("Starting Server") 
        self.clients={}
        
        # Task
        taskMgr.add(self.update, 'server_update') 
        
        log.debug("Server started")
        
    #tasks
    def update(self, task):
        dt = globalClock.getDt()        
        return task.cont    
