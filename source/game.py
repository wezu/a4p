from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

from client import Client
from server import Server
from network import Network
from masterserver import Masterserver
from world import World

import traceback

class Game(DirectObject):
    def __init__(self):

        #a task chain for loading things in the background
        taskMgr.setupTaskChain('background_chain', numThreads = 1)

        #in all game modes a world, a network and a server is needed
        self.world=World()
        #self.net=Network()
        self.server=Server(self.world)

        if cfg['game-mode']=='normal':
            self.client=Client()

