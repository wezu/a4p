from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from vfx import Vfx

#Helper functions
def _pos2d(x,y):
    return Point3(x,0,-y)
    
def _rec2d(width, height):
    return (-width, 0, 0, height)
    
def _resetPivot(frame):
    size=frame['frameSize']    
    frame.setPos(-size[0], 0, -size[3])        
    frame.flattenLight()

class MainMenu(DirectObject):
    def __init__(self, ui):
        self.ui=ui
        #3D-ish background for the main menu
        #base.cam.setZ(8)
        base.cam.setPos(173.453, 8.02785, 143.622)
        base.cam.setHpr(92.2724, -28.5096, -58.8269)
        
        self.rings=[]
        for i in range(5):
            tex=path+"gui/ring{0}.png".format(4-i)
            self.rings.append(self._makeRing(tex,(i+1)*12, i))            

        self.elements={}
            
        #frame for the main menu        
        self.elements['frame_top_left']=self._makeFrame(path+'gui/corner_left_up.png', ui.top_left, (0,0))
        self.elements['frame_top_right']=self._makeFrame(path+'gui/corner_right_up.png', ui.top_right, (-128,0))
        self.elements['frame_bottom_left']=self._makeFrame(path+'gui/corner_left_down.png', ui.bottom_left, (0,-128))
        self.elements['frame_bottom_right']=self._makeFrame(path+'gui/corner_right_down.png', ui.bottom_right, (-128,-128))

        #close button
        self.elements['close_button']=self._makeButton('', (64, 64), path+'gui/empty_64.png', path+'gui/close.png', self.onExit, ui.top_right, (-64,0), 4)       
        #tutorial button
        self.elements['tutorial_button']=self._makeButton('Tutorial', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showTutorialMenu, ui.top_left, (0,0), 2, ui.font_special )
        #host button
        self.elements['host_button']=self._makeButton('Host', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showHostMenu, ui.top, (-128,0), 0, ui.font_special )
        #join button
        self.elements['join_button']=self._makeButton('Join', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showJoinMenu, ui.top, (-128,128), 1, ui.font_special )
        #options
        self.elements['options_button']=self._makeButton('Options', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showOptionMenu, ui.top_left, (0,128), 3, ui.font_special )
        
        #link-bar
        self.elements['link_bar_1']=self._makeFrame(path+'gui/bar2.png', ui.top_left, (128,108), (128, 32))
        self.elements['link_bar_1'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_bar_1'].hide()
        self.elements['link_line_1']=self._makeFrame(path+'gui/line1.png', ui.top_left, (128+128,108), (1, 32))
        self.elements['link_line_1'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_line_1'].hide()
        
        self.elements['link_bar_2']=self._makeFrame(path+'gui/bar2.png', ui.top, (0,108), (128, 32))
        self.elements['link_bar_2'].hide()
        self.elements['link_bar_2'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_line_2']=self._makeFrame(path+'gui/line1.png', ui.top, (128,108), (1, 32))
        self.elements['link_line_2'].hide()
        self.elements['link_line_2'].setColor(0.33, 0.56, 1.0, 1.0)
        
        #top of the content frame
        self.elements['content_frame_1']=self._makeFrame(path+'gui/frame5.png', ui.top_right, (-256,62), (256, 256))
        self.elements['content_frame_1'].hide()
        self.elements['content_frame_1'].setColor(0.33, 0.56, 1.0, 1.0)
        #center of the content frame
        self.elements['content_frame_2']=self._makeFrame(path+'gui/frame7.png', ui.top_right, (-256,62+256), (256, 1))
        self.elements['content_frame_2'].hide()
        self.elements['content_frame_2'].setColor(0.33, 0.56, 1.0, 1.0)
        #bottom of the content frame
        self.elements['content_frame_3']=self._makeFrame(path+'gui/frame6.png', ui.bottom_right, (-256,-64-8), (256, 64))
        self.elements['content_frame_3'].hide()
        self.elements['content_frame_3'].setColor(0.33, 0.56, 1.0, 1.0)
        #tooltip frame
        self.elements['tooltip_frame']=self._makeFrame(path+'gui/frame8.png', ui.top_right, (-256-234,-64-8+256+40), (256, 256))
        self.elements['tooltip_frame'].hide()
        self.elements['tooltip_frame'].setColor(0.33, 0.56, 1.0, 1.0)
        
        self.ingore_hover=[]
    
        self.setShader(path+'shaders/gui_v.glsl', path+'shaders/gui_f.glsl')
    
    def setShader(self, v_shader, f_shader):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        for element in self.elements.itervalues():
            element.setAttrib(shader_attrib)
        
    def showTutorialMenu(self):
        self.ingore_hover=[]
        self.hoverAllOut()
        self.onHoverIn(self.elements['tutorial_button'],ring_id= 2)
        self.elements['tutorial_button']['text_fg']=(0.33, 0.56, 1.0, 1.0)
        self.elements['tutorial_button'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_bar_1'].show()
        self.elements['link_bar_1']['frameTexture']=loader.loadTexture(path+'gui/bar1.png')
        self.elements['link_line_1'].show()
        self.elements['content_frame_1'].show()
        self.elements['content_frame_2'].show()
        self.elements['content_frame_3'].show()
        self.elements['link_line_2'].hide()
        self.elements['link_bar_2'].hide()
        self.elements['tooltip_frame'].show()
        if not self.elements['tutorial_button'] in self.ingore_hover:
            self.ingore_hover.append(self.elements['tutorial_button'])
    
    def showOptionMenu(self):
        self.ingore_hover=[]
        self.hoverAllOut()
        self.onHoverIn(self.elements['options_button'], ring_id= 3)
        self.elements['options_button']['text_fg']=(0.33, 0.56, 1.0, 1.0)
        self.elements['options_button'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_bar_1'].show()
        self.elements['link_bar_1']['frameTexture']=loader.loadTexture(path+'gui/bar2.png')
        self.elements['link_line_1'].show()
        self.elements['content_frame_1'].show()
        self.elements['content_frame_2'].show()
        self.elements['content_frame_3'].show() 
        self.elements['link_line_2'].hide()
        self.elements['link_bar_2'].hide()
        self.elements['tooltip_frame'].hide()
        if not self.elements['options_button'] in self.ingore_hover:
            self.ingore_hover.append(self.elements['options_button'])
    
    def showHostMenu(self):
        self.ingore_hover=[]
        self.hoverAllOut()
        self.onHoverIn(self.elements['host_button'], ring_id= 0)
        self.elements['host_button']['text_fg']=(0.33, 0.56, 1.0, 1.0)
        self.elements['host_button'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_bar_2'].show()
        self.elements['link_bar_2']['frameTexture']=loader.loadTexture(path+'gui/bar1.png')
        self.elements['link_line_2'].show()
        self.elements['content_frame_1'].show()
        self.elements['content_frame_2'].show()
        self.elements['content_frame_3'].show()
        self.elements['link_line_1'].hide()
        self.elements['link_bar_1'].hide()
        self.elements['tooltip_frame'].hide()        
        if not self.elements['host_button'] in self.ingore_hover:
            self.ingore_hover.append(self.elements['host_button'])
        
    def showJoinMenu(self):
        self.ingore_hover=[]
        self.hoverAllOut()
        self.onHoverIn(self.elements['join_button'], ring_id=1)
        self.elements['join_button']['text_fg']=(0.33, 0.56, 1.0, 1.0)
        self.elements['join_button'].setColor(0.33, 0.56, 1.0, 1.0)
        self.elements['link_bar_2'].show()
        self.elements['link_bar_2']['frameTexture']=loader.loadTexture(path+'gui/bar2.png')
        self.elements['link_line_2'].show()
        self.elements['content_frame_1'].show()
        self.elements['content_frame_2'].show()
        self.elements['content_frame_3'].show()
        self.elements['link_line_1'].hide()
        self.elements['link_bar_1'].hide() 
        self.elements['tooltip_frame'].hide()       
        if not self.elements['join_button'] in self.ingore_hover:
            self.ingore_hover.append(self.elements['join_button'])
            
    def resize(self, window_x, window_y):
        #link_line_1 starts at x=256 and ends at window_x-256
        self.elements['link_line_1'].setScale(window_x-512, 1, 1)        
        #link_line_1 starts at x=window_x/2+128 and ends at window_x-256
        self.elements['link_line_2'].setScale(window_x/2-384, 1, 1)
        #content_frame_2 starts at 318 and ends at window_y-72
        self.elements['content_frame_2'].setScale(1, 1, window_y-390)
        
    def hide(self):
        for element in self.elements.itervalues():
            element.hide()
        for ring in self.rings:
            ring[0].hide()
            ring[1].pause()
            ring[2].hide()
        
    def show(self):
        for element in self.elements.itervalues():
            element.show()
        for ring in self.rings:
            ring[0].show()
            ring[1].loop()
            ring[2].show()
                
    def onExit(self):        
        messenger.send('exit-event')
    
    def onCmd(self, frame, cmd, event=None):
        cmd()
        
        
    def hoverAllOut(self):
        self.onHoverOut(self.elements['close_button'], path+'gui/empty_64.png', 4)
        self.onHoverOut(self.elements['tutorial_button'], path+'gui/frame2b.png', 2)
        self.onHoverOut(self.elements['host_button'], path+'gui/frame2b.png', 0)
        self.onHoverOut(self.elements['join_button'], path+'gui/frame3b.png', 1)
        self.onHoverOut(self.elements['options_button'], path+'gui/frame3b.png', 3)
    
    def onHoverIn(self, frame, tex=None, ring_id=None, event=None):
        if frame in self.ingore_hover:
            return
        if tex:    
            frame['frameTexture']=loader.loadTexture(tex) 
        frame['text_fg']=(0.94, 0.0, 0.1, 1.0) 
        frame.setColor(0.94, 0.0, 0.1, 1.0) 
        self.rings[ring_id][0].setColor(0.94, 0.0, 0.1, 1.0)        
        LerpPosInterval(self.rings[ring_id][0], 0.2, (0,0, 5.0)).start()
        if self.rings[ring_id][2]:
            self.rings[ring_id][2].setColor((1.0, 0.0, 0.0, 1.0))
            self.rings[ring_id][2].setForce('up', 1)
            self.rings[ring_id][2].setForce('down', 0)
    
    def onHoverOut(self, frame, tex=None, ring_id=None, event=None):
        if frame in self.ingore_hover:
            return
        if tex:
            frame['frameTexture']=loader.loadTexture(tex)
        frame['text_fg']=(0.33, 0.894, 1.0, 1.0)        
        frame.setColor(0.33, 0.894, 1.0, 1.0)  
        self.rings[ring_id][0].setColor(0.33, 0.894, 1.0, 1.0) 
        LerpPosInterval(self.rings[ring_id][0], 0.2, (0,0, 0.0)).start()
        if self.rings[ring_id][2]:
            #self.rings[ring_id][2].getParticlesList()[0].renderer.setColor((0.33, 0.894, 1.0, 1.0))
            self.rings[ring_id][2].setColor((0.33, 0.894, 1.0, 1.0))
            self.rings[ring_id][2].setForce('up', 0)
            self.rings[ring_id][2].setForce('down', 1)
            
    def _makeButton(self, text, size, tex, hover_tex, cmd, parent, offset, ring_id=None, font=None):
        if font is None:
            font=self.ui.font            
        frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                frameColor=(1,1,1,1.0),
                                text=text,  
                                frameTexture=tex,                               
                                text_scale=32,
                                text_font=font,
                                text_align=TextNode.ACenter,
                                text_pos=(-size[0]/2,size[1]/2-4),
                                text_fg=(0.33, 0.894, 1.0, 1.0), 
                                state=DGG.NORMAL, 
                                parent=parent)  
        _resetPivot(frame) 
        frame.setPos(_pos2d(offset[0],offset[1]))
        frame.setColor(0.33, 0.894, 1.0, 1.0)    
        frame.setTransparency(TransparencyAttrib.MAlpha) 
        frame.bind(DGG.WITHOUT, self.onHoverOut,[frame, tex, ring_id])  
        frame.bind(DGG.WITHIN, self.onHoverIn, [frame, hover_tex, ring_id])        
        frame.bind(DGG.B1PRESS, self.onCmd, [frame, cmd])
        return frame
        
    def _makeFrame(self, tex, parent, offset, size=(128, 128)):
        frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                frameColor=(1,1,1,1),
                                frameTexture=tex, 
                                parent=parent)  
        _resetPivot(frame) 
        frame.setPos(_pos2d(offset[0],offset[1]))    
        frame.setColor(0.33, 0.894, 1.0, 1.0)
        frame.setTransparency(TransparencyAttrib.MAlpha)
        return frame
            
    def _makeRing(self, tex_path, time, z):
        cm = CardMaker("plane")
        cm.setFrame(-30, 30, -30, 30)
        ring_plane=render.attachNewNode(cm.generate())
        tex=loader.loadTexture(tex_path)
        ring_plane.setTexture(tex)
        #ring_plane.setTransparency(TransparencyAttrib.MAlpha, 1)
        attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
        ring_plane.setAttrib(attrib)        
        #ring_plane.setDepthOffset(4-z)
        #ring_plane.setBin("fixed", 20-z)
        ring_plane.setDepthTest(False)
        ring_plane.setDepthWrite(False)
        ring_plane.setPos(0,0,0)
        ring_plane.setHpr(0, -90, 0)
        ring_plane.setColor(0.33, 0.894, 1.0, 1.0)                
        particle=Vfx('menu_ring', radius=12+z+(z*3), parent=ring_plane, color=(0.33, 0.894, 1.0, 1.0) )
        interval=LerpHprInterval(ring_plane, time,(0, -90, 360))
        interval.loop()
        return (ring_plane, interval, particle)        
        
