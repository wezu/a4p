from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

from filters import Filters
from ui import UserInterface
from audio import Audio
from lightmanager import LightManager

import traceback
import json
from collections import deque
import random
class Client(DirectObject):
    """
    Client class handels gui/input audio and rendering
    """
    def __init__(self):
        log.debug('Starting Client')
        #open a window... but first set all the needed props
        wp=self.loadWindoProperites()
        #open the window
        base.openMainWindow(props = wp)
        base.setBackgroundColor(0.06, 0.1, 0.12, 1)
        #base.disableMouse()
        base.enableParticles()

        #needed to determine what window event fired
        self.window_focused=base.win.getProperties().getForeground()
        self.window_x=base.win.getXSize()
        self.window_y=base.win.getYSize()
        self.window_minimized=base.win.getProperties().getMinimized()

        #filter manager, post process
        self.filters=Filters()
        if cfg['use-filters']:
            self.filters.setupFilters()
        elif cfg['use-fxaa']:
            self.filters.setupFxaa()

        #audio sound effects (sfx) + music
        self.audio=Audio()
        self.audio.setMusic('background')
        self.audio.playMusic()

        #light manager
        self.lights=LightManager()

        #setup the user interface (gui+key/mouse bind)
        self.ui=UserInterface()

        #some vars used later
        self.map_name=None
        self.loading_status=set()
        self.level_root=render.attachNewNode('level_root')
        self.level_root.hide()
        self.skyimg=PNMImage(path+'data/sky_grad.png')

        #events
        base.win.setCloseRequestEvent('exit-event')
        self.accept('exit-event',self.onClientExit)
        self.accept( 'window-event', self.onWindowEvent)
        self.accept( 'window-reset', self.onWindowReset)
        self.accept( 'client-mouselock', self.setMouseLock)
        self.accept( 'load-level', self.onLevelLoad)
        self.accept( 'loading-done', self.onLoadingDone)

        # Task
        taskMgr.add(self.update, 'client_update')

        log.debug('Client started')

    def doSomeStuffTsk(self, task):
        x=deque(range(5000))
        for i in xrange(999):
           random.shuffle(x)
           print i, x[0]
        print 'done'
        return task.done

    def setMouseLock(self, lock):
        wp = WindowProperties.getDefault()
        if lock:
            wp.setMouseMode(WindowProperties.M_confined)
        else:
            wp.setMouseMode(WindowProperties.M_relative)
        if not cfg['use-os-cursor']:
            wp.setCursorHidden(True)
        base.win.requestProperties(wp)

    def loadWindoProperites(self):
        #check if we can open a fullscreen window at the requested size
        if cfg['fullscreen']:
            mods=[]
            for mode in base.pipe.getDisplayInformation().getDisplayModes():
                mods.append([mode.width, mode.height])
            if list(cfg['win-size']) not in mods:
                cfg['fullscreen']=False
                log.warning('Can not open fullscreen window at '+str(cfg['win-size']))

        #the window props should be set by this time, but make sure
        wp = WindowProperties.getDefault()
        try:
            wp.setUndecorated(cfg['undecorated'])
            wp.setFullscreen(cfg['fullscreen'])
            wp.setSize(cfg['win-size'][0],cfg['win-size'][1])
            wp.setFixedSize(cfg['win-fixed-size'])
        except:
            log.warning('Failed to set window properties, Traceback:')
            for error in traceback.format_exc().splitlines()[1:]:
                log.warning(error.strip())

        #these probably won't be in the config (?)
        wp.setOrigin(-2,-2)
        wp.setTitle('A4P')
        if not cfg['use-os-cursor']:
            wp.setCursorHidden(True)
        return wp

    def blendPixels(self, p1, p2, blend):
        c1=[p1[0]/255.0,p1[1]/255.0,p1[2]/255.0, p1[3]/255.0]
        c2=[p2[0]/255.0,p2[1]/255.0,p2[2]/255.0, p2[3]/255.0]
        return VBase4F( c1[0]*blend+c2[0]*(1.0-blend), c1[1]*blend+c2[1]*(1.0-blend), c1[2]*blend+c2[2]*(1.0-blend), c1[3]*blend+c2[3]*(1.0-blend))

    def setTime(self, time):
        self.clock=time
        sunpos=min(0.5, max(-0.5,(time-12.0)/14.0))
        render.setShaderInput('sunpos', sunpos)
        x1=int(time)
        x2=x1-1

        x1=min(23, max(0,x1))
        x2=min(23, max(0,x2))

        if x2<0:
            x2=0
        blend=time%1.0

        p1=self.skyimg.getPixel(x1, 0)
        p2=self.skyimg.getPixel(x2, 0)
        sunColor=self.blendPixels(p1, p2, blend)
        sunColor[0]=sunColor[0]
        sunColor[1]=sunColor[1]
        sunColor[2]=sunColor[2]
        p1=self.skyimg.getPixel(x1, 1)
        p2=self.skyimg.getPixel(x2, 1)
        skyColor=self.blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 2)
        p2=self.skyimg.getPixel(x2, 2)
        cloudColor=self.blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 3)
        p2=self.skyimg.getPixel(x2, 3)
        fogColor=self.blendPixels(p1, p2, blend)
        fogColor[3]=(abs(sunpos)*0.005+0.001)

        if time<6.0 or time>18.0:
            p=15.0
        else:
            p=sunpos*-180.0
        p=min(60.0, max(-60.0,p))


        self.lights.directionalLight(Vec3(0,p,0), sunColor)

        render.setShaderInput("sunColor",sunColor)
        render.setShaderInput("skyColor",skyColor)
        render.setShaderInput("cloudColor",cloudColor)
        render.setShaderInput("fog", fogColor)

    def loadLevel(self, task):
        log.debug('Client loading level...')
        with open(path+'maps/'+self.map_name+'.json') as f:
            values=json.load(f)
        #set the time
        self.setTime(values['level']['time'])
        #load visible objects
        for obj in values['objects']:
            mesh=loader.loadModel(path+obj['model'])
            mesh.reparentTo(self.level_root)
            mesh.setPosHpr(tuple(obj['pos']), tuple(obj['hpr']))
            for name, value in obj['shader_inputs'].iteritems():
                print name, value
                if isinstance(value, basestring):
                    mesh.setShaderInput(str(name), loader.loadTexture(path+value))
                if isinstance(value, float):
                    mesh.setShaderInput(str(name), value)
                if isinstance(value, list):
                    if len(value) == 2:
                        mesh.setShaderInput(str(name), Vec2(value[0], value[1]))
                    elif len(value) == 3:
                        mesh.setShaderInput(str(name), Vec3(value[0], value[1], value[2]))
                    elif len(value) == 3:
                        mesh.setShaderInput(str(name), Vec4(value[0], value[1], value[2], value[3]))
            mesh.setShader(Shader.load(Shader.SLGLSL, obj['vertex_shader'],obj['fragment_shader']))
        #set the music
        self.audio.setMusic(values['level']['music'])

        messenger.send('loading-done', ['client'])
        return task.done

    #events
    def onLoadingDone(self, target):
        log.debug(str(target)+' loading done')
        self.loading_status.add(target)
        if self.loading_status == set(['client', 'server', 'world']):
            self.level_root.show()
            self.ui.main_menu.hide()

    def onLevelLoad(self, map_name):
        self.map_name=map_name
        taskMgr.doMethodLater(1.0, self.loadLevel, 'client_loadLevel_task', taskChain = 'background_chain')
        #taskMgr.add(self.loadLevel, 'client_loadLevel_task', taskChain = 'background_chain')
        #the client needs to load/setup:
        # -visible geometry
        # -enviroment (skybox/dome + sunlight diection + fog + ???)
        # -water plane
        # -unmovable (point)light sources
        # -unmovable vfx
        # -the player droid

    def onClientExit(self):
        log.debug('Client exit')
        self.audio.cleanup()
        app.exit()

    def onWindowReset(self):
        wp=self.loadWindoProperites()
        base.win.requestProperties(wp)

    def onWindowMinimize(self):
        self.window_minimized=base.win.getProperties().getMinimized()
        log.debug('window-event: Minimize is '+str(self.window_minimized))

    def onWindowFocus(self):
        self.window_focused=base.win.getProperties().getForeground()
        log.debug('window-event: Focus set to '+str(self.window_focused))
        if cfg['pause-on-focus-lost']:
            if not self.window_focused:
                self.audio.pauseMusic()
                base.win.setActive(False)
            else:
                self.audio.resumeMusic()
                base.win.setActive(True)

    def onWindowResize(self):
        self.window_x=base.win.getXSize()
        self.window_y=base.win.getYSize()
        log.debug('window-event: Resize')
        self.filters.update()
        self.ui.updateGuiNodes()

    def onWindowEvent(self,window=None):
        if window is not None: # window is none if panda3d is not started
            if self.window_x!=base.win.getXSize() or self.window_y!=base.win.getYSize():
                self.onWindowResize()
            elif window.getProperties().getMinimized() !=  self.window_minimized:
                self.onWindowMinimize()
            elif window.getProperties().getForeground() !=  self.window_focused:
                self.onWindowFocus()

    #tasks
    def update(self, task):
        dt = globalClock.getDt()
        render.setShaderInput('camera_pos', base.cam.getPos(render))
        return task.cont
