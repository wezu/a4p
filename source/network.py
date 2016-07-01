from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import socket
from rencode import dumps as pack
from rencode import loads as unpack

from collections import namedtuple

SERVER_PORT=5005

MSG_HEADER_DEBUG=0
MSG_HEADER_LOGIN=1
MSG_HEADER_LOGOUT=2
MSG_HEADER_HPR_POS_UPDATE=3
MSG_HEADER_STAT_UPDATE=4
MSG_HEADER_SPAWN=5
MSG_HEADER_KICK=6
MSG_HEADER_ERROR=7

Datagram=namedtuple('Datagram','header source number data')

class Network(DirectObject):
    def __init__(self):
        self.targets={}
        self.next_target_id=0

        self.reading_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reading_socket.bind(('',SERVER_PORT))
        self.reading_socket.setblocking(0)

        self.writing_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #event handling

        # Task
        taskMgr.add(self.listen, 'network_listen')

    def addTarget(self, IP, port):
        log.debug('Network target added:'+str(IP)+':'+str(port))
        self.targets[self.next_target_id]=(IP, port)
        self.next_target_id+=1
        return self.next_target_id-1

    def removeTarget(self, target_id):
        del self.targets[target_id]

    def send(self, target_id, msg):
        self.writing_socket.sendto(pack(msg, True), self.targets[target_id])

    def sendToAll(self, msg):
        for target in self.targets.values():
            self.writing_socket.sendto(msg, target)


    def listen(self, task):
        #try to read some data from the socket
        raw_data=None
        try:
            raw_data = self.reading_socket.recvfrom(1024)
        except:
            pass
        #if we got some data try to decode it
        if raw_data:
            raw_msg=raw_data[0]
            IP=raw_data[1][0]
            port=raw_data[1][1]
            try:
                msg=unpack(raw_msg)
                assert isinstance(msg,  tuple) #the msg MUST be a tuple
                #the msg must have this format: (MSG_HEADER, MSG_SOURCE, MSG_NUMBER, MSG_DATA)
                assert len(msg)==4
                data=Datagram(*msg)
            except:
                log.warning('error decoding msg: '+raw_msg)
                return task.cont

            if data.header==MSG_HEADER_LOGIN:
                messenger.send('login',[IP, port, data.source])


        return task.cont


if __name__ == '__main__':

    class NullLog():
        def __init__(self):
            pass
        def  warning(self, txt):
            pass
        def  debug(self, txt):
            pass
    log=NullLog()
    from direct.showbase import ShowBase
    base = ShowBase.ShowBase()
    n=Network()
    target=n.addTarget( 'localhost', 5005)
    n.send(target, (MSG_HEADER_LOGIN, 'client1', 0, 0))
    base.run()
