from collections import namedtuple

ServerData=namedtuple('ServerData','IP port game_type')

class Masterserver():
    def __init__(self):
        self.servers={}

    def getServers(self):
        return self.servers

    def addServer(self, IP, port, game_type, name):
        self.servers[name]=ServerData(IP, port, game_type)

    def removeServer(self, name):
        del self.servers[name]
