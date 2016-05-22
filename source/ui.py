from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from mainmenu import MainMenu


#Helper functions
def _pos2d(x,y):
    return Point3(x,0,-y)

def _rec2d(width, height):
    return (-width, 0, 0, height)

def _resetPivot(frame):
    size=frame['frameSize']
    frame.setPos(-size[0], 0, -size[3])
    frame.flattenLight()

class UserInterface(DirectObject):
    def __init__(self):
        log.debug('Starting UserInterface')

        #load fonts
        self.font = loader.loadFont(path+cfg['font-default'])
        self.font.setPixelsPerUnit(32)
        self.font.setMinfilter(Texture.FTNearest )
        self.font.setMagfilter(Texture.FTNearest )

        self.font_special = loader.loadFont(path+cfg['font-special'])
        self.font_special.setPixelsPerUnit(32)
        self.font_special.set_outline((1, 1, 1, 0.5), 4, 0.6)
        self.font_special.setMinfilter(Texture.FTNearest )
        self.font_special.setMagfilter(Texture.FTNearest )

        #set nodes for gui placement
        self.top_left=pixel2d.attachNewNode('TopLeft')
        self.top_right=pixel2d.attachNewNode('TopRight')
        self.bottom_right=pixel2d.attachNewNode('BottomRight')
        self.bottom_left=pixel2d.attachNewNode('BottomLeft')
        self.top=pixel2d.attachNewNode('Top')
        self.bottom=pixel2d.attachNewNode('Bottom')
        self.left=pixel2d.attachNewNode('Left')
        self.right=pixel2d.attachNewNode('Right')
        self.center=pixel2d.attachNewNode('Center')

        pixel2d.setShaderInput('strip', loader.loadTexture(path+'gui/strip.png'))

        #make the main menu
        self.main_menu=MainMenu(self)

        if cfg['show-frame-rate-meter']:
            self.fps_node=NodePath(base.frameRateMeter)
            self.fps_node.wrtReparentTo(self.top_right)
            self.fps_node.setPos(-128, 0, 0)

        #mouse cursor
        self.cursor=self.main_menu._makeFrame(path+'gui/pointer1.png', pixel2d, (0,0), (32, 32))

        #place the nodes at the right places
        self.updateGuiNodes()

        # Task
        taskMgr.add(self.update, 'ui_update')

    #tasks
    def update(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.cursor.show()
            mpos = base.mouseWatcherNode.getMouse()
            pos2d=Point3(mpos.getX() ,0, mpos.getY())
            self.cursor.setPos(pixel2d.getRelativePoint(render2d, pos2d))
        else:
            self.onWindowMouseOut()
        return task.cont

    def onWindowMouseOut(self):
        self.main_menu.hoverAllOut()
        self.cursor.hide()

    def updateGuiNodes(self):
        winX = base.win.getXSize()
        winY = base.win.getYSize()
        self.top_left.setPos(_pos2d(0,0))
        self.top_right.setPos(_pos2d(winX,0))
        self.bottom_right.setPos(_pos2d(winX,winY))
        self.bottom_left.setPos(_pos2d(0,winY))
        self.top.setPos(_pos2d(winX/2,0))
        self.bottom.setPos(_pos2d(winX/2,winY))
        self.left.setPos(_pos2d(0,winY/2))
        self.right.setPos(_pos2d(winX,winY/2))
        self.center.setPos(_pos2d(winX/2,winY/2))
        self.main_menu.resize(winX, winY)
