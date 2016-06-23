from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from mainmenu import MainMenu
from ingamemenu import InGameMenu

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
    """
    Handels player input, be it via a gui, keys or mouse movment
    """
    def __init__(self):
        log.debug('Starting UserInterface')

        #load fonts
        self.font = loader.loadFont(path+cfg['font-default'])
        self.font.setPixelsPerUnit(17)
        self.font.setMinfilter(Texture.FTNearest )
        self.font.setMagfilter(Texture.FTNearest )

        self.font_special = loader.loadFont(path+cfg['font-special'])
        self.font_special.setPixelsPerUnit(48)
        self.font_special.set_outline((1, 1, 1, 0.5),3, 0.6)
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

        #make the in-game menu
        self.in_game_menu=InGameMenu(self)
        self.in_game_menu.hide()

        if cfg['show-frame-rate-meter']:
            self.fps_node=NodePath(base.frameRateMeter)
            self.fps_node.wrtReparentTo(self.top_right)
            self.fps_node.setPos(-128, 0, 0)

        #mouse cursor
        cursor_tex=path+'gui/pointer1.png'
        if cfg['use-os-cursor']:
            cursor_tex=path+'gui/empty_64.png'
        self.cursor=self.main_menu.makeFrame(cursor_tex, pixel2d, (0,0), (32, 32))
        self.cursor_pos=(0,0,0)
        #place the nodes at the right places
        self.updateGuiNodes()

        #keybinding
        self.key_map={'back':False,
                    'fire':False,
                    'forward':False,
                    'left':False,
                    'right':False,
                    'sprint':False}


        # Task
        taskMgr.add(self.update, 'ui_update')

    #tasks
    def update(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.cursor.show()
            mpos = base.mouseWatcherNode.getMouse()
            self.cursor_pos=Point3(mpos.getX() ,0, mpos.getY())
            self.cursor.setPos(pixel2d.getRelativePoint(render2d, self.cursor_pos))
        else:
            self.onWindowMouseOut()
        return task.cont

    def onWindowMouseOut(self):
        if not self.cursor.isHidden():
            self.main_menu.hoverAllOut()
            self.cursor.hide()

    def hideSoftCursor(self):
        self.cursor['frameTexture']=loader.loadTexture(path+'gui/empty_64.png')

    def showSoftCursor(self):
        self.cursor['frameTexture']=loader.loadTexture(path+'gui/pointer1.png')

    def bindKeys(self):
        self.ignoreAll()
        self.accept(cfg['key-back'], self.key_map.__setitem__, ["back", True])
        self.accept(cfg['key-fire'], self.key_map.__setitem__, ["fire", True])
        self.accept(cfg['key-forward'], self.key_map.__setitem__, ["forward", True])
        self.accept(cfg['key-left'], self.key_map.__setitem__, ["left", True])
        self.accept(cfg['key-right'], self.key_map.__setitem__, ["right", True])
        self.accept(cfg['key-sprint'], self.key_map.__setitem__, ["sprint", True])
        self.accept(cfg['key-back']+'-up', self.key_map.__setitem__, ["back", False])
        self.accept(cfg['key-fire']+'-up', self.key_map.__setitem__, ["fire", False])
        self.accept(cfg['key-forward']+'-up', self.key_map.__setitem__, ["forward", False])
        self.accept(cfg['key-left']+'-up', self.key_map.__setitem__, ["left", False])
        self.accept(cfg['key-right']+'-up', self.key_map.__setitem__, ["right", False])
        self.accept(cfg['key-sprint']+'-up', self.key_map.__setitem__, ["sprint", False])

        #cfg['key-zoom']
        #cfg['key-gun1']
        #cfg['key-gun2']
        #cfg['key-gun3']
        #cfg['key-menu']
        #cfg['key-orders']

        self.accept(cfg['key-menu'], self.in_game_menu.showMenu)
        self.accept(cfg['key-orders'], self.in_game_menu.showOrders)



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
