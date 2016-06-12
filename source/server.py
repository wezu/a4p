from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from collections import namedtuple
import json

ClientData=namedtuple('ClientData','name IP port')

class Server(DirectObject):
    def __init__(self, world):
        log.debug('Starting Server')
        self.world=world

        self.clients={}

        # Task
        taskMgr.add(self.update, 'server_update')

        #events
        self.accept('server-start',self.start)
        self.accept('server-stop',self.stop)
        self.accept( 'load-level', self.onLevelLoad)

        log.debug('Server started')

    def loadLevel(self, task):
        log.debug('Server loading level...')
        with open(path+'maps/'+self.map_name+'.json') as f:
            values=json.load(f)
        #the server needs to load/setup:
        # -game rules
        # -scriplets for special objects
        messenger.send('loading-done', ['server'])
        return task.done

    def onLevelLoad(self, map_name):
        self.map_name=map_name
        taskMgr.add(self.loadLevel, 'server_loadLevel_task', taskChain = 'background_chain')


    def start(self):
        self.accept('load-level',self.loadLevel)

    def stop(self):
        self.ignore('load-level')

    #tasks
    def update(self, task):
        dt = globalClock.getDt()
        return task.cont

