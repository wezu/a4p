from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

from filters import Filters
from ui import UserInterface

import traceback

class Client(DirectObject):
    def __init__(self):
        log.debug("Starting Client") 
        #open a window... but first set all the needed props
        #check if we can open a fullscreen window at the requested size
        if cfg['fullscreen']:
            mods=[]
            for mode in base.pipe.getDisplayInformation().getDisplayModes():
                mods.append([mode.width, mode.height])
            if cfg['win-size'] not in mods:
                cfg['fullscreen']=False
                log.warning("Can't open fullscreen window at "+str(cfg['win-size']))   

        #the window props should be set by this time, but make sure 
        wp = WindowProperties.getDefault() 
        try:
            wp.setUndecorated(cfg['undecorated'])
            wp.setFullscreen(cfg['fullscreen'])
            wp.setSize(cfg['win-size'][0],cfg['win-size'][1])   
            wp.setFixedSize(cfg['win-fixed-size'])
        except:
            log.warning("Failed to set window properties, Traceback:") 
            for error in traceback.format_exc().splitlines()[1:]:
                log.warning(error.strip())
               
        #these probably won't be in the config (?)
        wp.setOrigin(-2,-2)
        wp.setTitle("A4P")
        wp.setCursorHidden(True)
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
            
        #setup the user interface (gui+key/mouse bind)    
        self.ui=UserInterface()
            
        #events
        base.win.setCloseRequestEvent('exit-event')        
        self.accept('exit-event',self.onClientExit)   
        self.accept( 'window-event', self.onWindowEvent)
                
        # Task
        taskMgr.add(self.update, 'client_update') 
        
        log.debug("Client started")        
        
    #events        
    def onClientExit(self):
        log.debug("Client exit")
        app.exit()
   
    def onWindowMinimize(self):
        self.window_minimized=base.win.getProperties().getMinimized()
        log.debug("window-event: Minimize is "+str(self.window_minimized))
        
    def onWindowFocus(self):  
        self.window_focused=base.win.getProperties().getForeground()  
        log.debug("window-event: Focus set to "+str(self.window_focused))
    
    def onWindowResize(self):
        self.window_x=base.win.getXSize()
        self.window_y=base.win.getYSize()
        log.debug("window-event: Resize")
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
        render.setShaderInput("camera_pos", base.cam.getPos(render))       
        return task.cont
