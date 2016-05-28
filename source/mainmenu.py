from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.stdpy.file import listdir

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
    """
    Main Menu, the menu shown befor starting a match or between them
    """
    def __init__(self, ui):
        self.ui=ui
        #3D-ish background for the main menu
        base.cam.setPos(173.453, 8.02785, 143.622)
        base.cam.setHpr(92.2724, -28.5096, -58.8269)

        self.rings=[]
        for i in range(5):
            tex=path+'gui/ring{0}.png'.format(4-i)
            self.rings.append(self._makeRing(tex,(i+1)*12, i))

        self.elements={}

        #frame for the main menu
        self.elements['frame_top_left']=self.makeFrame(path+'gui/corner_left_up.png', ui.top_left, (0,0))
        self.elements['frame_top_right']=self.makeFrame(path+'gui/corner_right_up.png', ui.top_right, (-128,0))
        self.elements['frame_bottom_left']=self.makeFrame(path+'gui/corner_left_down.png', ui.bottom_left, (0,-128))
        self.elements['frame_bottom_right']=self.makeFrame(path+'gui/corner_right_down.png', ui.bottom_right, (-128,-128))

        #close button
        self.elements['close_button']=self.makeButton('', (64, 64), path+'gui/empty_64.png', path+'gui/close.png', self.onExit, ui.top_right, (-64,0), 4)
        #tutorial button
        self.elements['tutorial_button']=self.makeButton('TUTORIAL', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showTutorialMenu, ui.top_left, (0,0), 2, ui.font_special )
        #host button
        self.elements['host_button']=self.makeButton('HOST', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showHostMenu, ui.top, (-128,0), 0, ui.font_special )
        #join button
        self.elements['join_button']=self.makeButton('JOIN', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showJoinMenu, ui.top, (-128,128), 1, ui.font_special )
        #options
        self.elements['option_button']=self.makeButton('OPTIONS', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showOptionMenu, ui.top_left, (0,128), 3, ui.font_special )

        #link-bar
        self.elements['link_bar_1']=self.makeFrame(path+'gui/bar2.png', ui.top_left, (128,108), (128, 32))
        self.elements['link_bar_1'].setColor(cfg['ui_color3'])
        self.elements['link_bar_1'].hide()
        self.elements['link_line_1']=self.makeFrame(path+'gui/line1.png', ui.top_left, (128+128,108), (1, 32))
        self.elements['link_line_1'].setColor(cfg['ui_color3'])
        self.elements['link_line_1'].hide()

        self.elements['link_bar_2']=self.makeFrame(path+'gui/bar2.png', ui.top, (0,108), (128, 32))
        self.elements['link_bar_2'].hide()
        self.elements['link_bar_2'].setColor(cfg['ui_color3'])
        self.elements['link_line_2']=self.makeFrame(path+'gui/line1.png', ui.top, (128,108), (1, 32))
        self.elements['link_line_2'].hide()
        self.elements['link_line_2'].setColor(cfg['ui_color3'])

        #top of the content frame
        self.elements['content_frame_1']=self.makeFrame(path+'gui/frame5.png', ui.top_right, (-256,62), (256, 256))
        self.elements['content_frame_1'].hide()
        self.elements['content_frame_1'].setColor(cfg['ui_color3'])
        #center of the content frame
        self.elements['content_frame_2']=self.makeFrame(path+'gui/frame7.png', ui.top_right, (-256,62+256), (256, 1))
        self.elements['content_frame_2'].hide()
        self.elements['content_frame_2'].setColor(cfg['ui_color3'])
        #bottom of the content frame
        self.elements['content_frame_3']=self.makeFrame(path+'gui/frame6.png', ui.bottom_right, (-256,-64-8), (256, 64))
        self.elements['content_frame_3'].hide()
        self.elements['content_frame_3'].setColor(cfg['ui_color3'])
        #tooltip frame
        self.elements['tooltip_frame']=self.makeFrame(path+'gui/frame8.png', ui.top_right, (-256-234,-64-8+256+40), (256, 256))
        self.elements['tooltip_frame'].hide()
        self.elements['tooltip_frame'].setColor(cfg['ui_color3'])

        self.ingore_hover=[]
        self.last_element_list=[]
        self.setShader(path+'shaders/gui_v.glsl', path+'shaders/gui_f.glsl')

        #we make a big canvas for all the buttons to fit, so we don't need to resize the canvas later
        #minimal canvas size is 14*64 (number of buttons * button size)
        self.canvas_size=14*64
        #all the known maps must also fit the canvas, we might as well look for them now
        self.known_levels=[]
        for map_file in listdir(path+'maps'):
            name=Filename(map_file)
            if  name.getExtension() == 'json':
                self.known_levels.append(name.getBasenameWoExtension())
        if len (self.known_levels) >13:
            self.canvas_size=len (self.known_levels)*64
        #scrolled frame for all the items
        self.elements['scrolled_frame']=DirectScrolledFrame(
                                                            canvasSize = _rec2d(256,self.canvas_size),
                                                            frameSize = _rec2d(272,448),
                                                            parent = ui.bottom_right,
                                                            frameColor=(1,1,1,0.0),
                                                            verticalScroll_manageButtons=False,
                                                            verticalScroll_frameColor=cfg['ui_color1'],
                                                            verticalScroll_frameSize=_rec2d(16,128),
                                                            verticalScroll_frameTexture=path+'gui/line2.png',
                                                            verticalScroll_relief=DGG.FLAT,
                                                            verticalScroll_resizeThumb=False,
                                                            verticalScroll_thumb_relief=DGG.FLAT,
                                                            verticalScroll_thumb_frameSize=_rec2d(16,64),
                                                            verticalScroll_thumb_frameColor=cfg['ui_color1'],
                                                            verticalScroll_thumb_frameTexture=path+'gui/thumb.png'
                                                            )
        _resetPivot(self.elements['scrolled_frame'])
        self.elements['scrolled_frame'].setPos(_pos2d(0,-48))
        self.elements['scrolled_frame'].setTransparency(TransparencyAttrib.MAlpha)
        self.elements['scrolled_frame'].hide()
        self.elements['scrolled_frame'].verticalScroll.incButton.hide()
        self.elements['scrolled_frame'].verticalScroll.decButton.hide()
        self.elements['scroll_canvas']=self.elements['scrolled_frame'].getCanvas()
        #all the options buttons
        self.elements['options_res']=self.makeSmallButton('Resolution', 0, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_music_vol']=self.makeSmallButton('Music Volume', 64, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_sound_vol']=self.makeSmallButton('Sound Volume', 64*2, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_shadows']=self.makeSmallButton('Shadows', 64*3, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_filters']=self.makeSmallButton('Special Effects', 64*4, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_mouse']=self.makeSmallButton('Mouse speed', 64*5, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_forward']=self.makeSmallButton('KEY: forward', 64*6, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_back']=self.makeSmallButton('KEY: back', 64*7, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_left']=self.makeSmallButton('KEY: left', 64*8, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_right']=self.makeSmallButton('KEY: right', 64*9, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_fire']=self.makeSmallButton('KEY: fire', 64*10, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_zoom']=self.makeSmallButton('KEY: zoom', 64*11, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_sprint']=self.makeSmallButton('KEY: sprint', 64*12, self.showOptionMenu, 'scroll_canvas')
        self.elements['options_key_menu']=self.makeSmallButton('KEY: show  menu', 64*13, self.showOptionMenu, 'scroll_canvas')

        for i, level in enumerate(self.known_levels):
            self.elements['level_'+level]=self.makeSmallButton(level, 64*i, self.showOptionMenu, 'scroll_canvas')
            self.elements['level_'+level].hide()

        self.accept('wheel_up', self.scroll, [-1])
        self.accept('wheel_down', self.scroll, [1])

    def scroll(self, direction):
        v=self.elements['scrolled_frame'].verticalScroll['value']
        self.elements['scrolled_frame'].verticalScroll['value']=v+direction*cfg['mouse-scroll-speed']

    def setShader(self, v_shader, f_shader):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        for element in self.elements.itervalues():
            element.setAttrib(shader_attrib)

    def _doDebugThing(self):
        """A function for doing some random testing stuff, do not use """
        messenger.send('audio-sfx',['large-explosion', (0, 0, 0)])

    def fadeIn(self, frame, to_color, from_color=(1, 1, 1, 0)):
        frame.show()
        frame.setColor(from_color)
        LerpColorInterval(frame, 0.3, to_color, blendType='easeInOut').start()

    def showContentFrame(self,line='link_line_1', bar='link_bar_1', tex='gui/bar1.png'):
        self.elements['link_line_1'].hide()
        self.elements['link_line_2'].hide()
        self.elements['link_bar_1'].hide()
        self.elements['link_bar_2'].hide()
        self.elements[bar]['frameTexture']=loader.loadTexture(path+tex)
        self.fadeIn(self.elements[line],cfg['ui_color3'])
        self.fadeIn(self.elements[bar],cfg['ui_color3'])
        self.fadeIn(self.elements['content_frame_1'],cfg['ui_color3'])
        self.fadeIn(self.elements['content_frame_2'],cfg['ui_color3'])
        self.fadeIn(self.elements['content_frame_3'],cfg['ui_color3'])
        self.fadeIn(self.elements['scrolled_frame'].verticalScroll.thumb,cfg['ui_color1'])
        self.elements['scrolled_frame'].show()

    def showMenu(self, main_button, ring_id, element_list):
        self.ingore_hover=[]
        self.hoverAllOut()
        self.fadeIn(self.elements[main_button], cfg['ui_color3'])
        self.elements['scrolled_frame'].verticalScroll['value']=0.0
        if ring_id is not None:
            self.rings[ring_id][0].setColor(cfg['ui_color3'])
            self.rings[ring_id][2].setColor(cfg['ui_color3'])
            self.rings[ring_id][2].setForce('up', 1)
            self.rings[ring_id][2].setForce('down', 0)
        if main_button=='tutorial_button':
            self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar1.png')
            self.showElements('level_','options_')
        if main_button=='host_button':
            self.showContentFrame(line='link_line_2', bar='link_bar_2', tex='gui/bar1.png')
            self.showElements('level_','options_')
        if main_button=='join_button':
            self.showContentFrame(line='link_line_2', bar='link_bar_2', tex='gui/bar2.png')
            self.showElements('hosts_',('options_','level_'))
        if main_button=='option_button':
            self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar2.png')
            self.showElements('options_', 'level_')
        for element in self.last_element_list:
            self.elements[element].hide()
        for element in element_list:
            self.fadeIn(self.elements[element],cfg['ui_color3'])

        self.ingore_hover.append(self.elements[main_button])
        self.last_element_list=element_list

    def showElements(self, show_pattern, hide_pattern, color=cfg['ui_color1']):
        if isinstance(hide_pattern, basestring):
            hide_pattern=[hide_pattern]
        for  name, frame in self.elements.iteritems():
            if name.startswith(show_pattern):
                self.fadeIn(frame, color)
            else:
                for pattern in hide_pattern:
                    if name.startswith(pattern):
                        frame.hide()

    def showTutorialMenu(self):
        self.showMenu('tutorial_button', 2, [])

    def showOptionMenu(self):
        self.showMenu('option_button', 3, [])

    def showHostMenu(self):
        self.showMenu('host_button', 0, [])

    def showJoinMenu(self):
        self.showMenu('join_button', 1, [])

    def resize(self, window_x, window_y):
        #link_line_1 starts at x=256 and ends at window_x-256
        self.elements['link_line_1'].setScale(window_x-512, 1, 1)
        #link_line_1 starts at x=window_x/2+128 and ends at window_x-256
        self.elements['link_line_2'].setScale(window_x/2-384, 1, 1)
        #content_frame_2 starts at 318 and ends at window_y-72
        self.elements['content_frame_2'].setScale(1, 1, window_y-390)
        #the scrolled frame is upsidedown or something (?)
        self.elements['scrolled_frame']['frameSize'] = _rec2d(272,window_y-152)
        #self.elements['scrolled_frame'].verticalScroll['frameSize']=_rec2d(16,1)

    def hide(self):
        for element in self.elements.itervalues():
            element.hide()
        for ring in self.rings:
            ring[0].hide()
            ring[1].pause()
            ring[2].hide()

    def show(self):
        self.elements['close_button'].show()
        self.elements['tutorial_button'].show()
        self.elements['host_button'].show()
        self.elements['join_button'].show()
        self.elements['option_button'].show()
        self.elements['frame_top_left'].show()
        self.elements['frame_top_right'].show()
        self.elements['frame_bottom_left'].show()
        self.elements['frame_bottom_right'].show()
        for ring in self.rings:
            ring[0].show()
            ring[1].loop()
            ring[2].show()

    def onExit(self):
        messenger.send('exit-event')

    def onCmd(self, frame, cmd, event=None):
        messenger.send('audio-sfx',['click'])
        cmd()

    def hoverAllOut(self):
        self.onHoverOut(self.elements['close_button'], path+'gui/empty_64.png', 4)
        self.onHoverOut(self.elements['tutorial_button'], path+'gui/frame2b.png', 2)
        self.onHoverOut(self.elements['host_button'], path+'gui/frame2b.png', 0)
        self.onHoverOut(self.elements['join_button'], path+'gui/frame3b.png', 1)
        self.onHoverOut(self.elements['option_button'], path+'gui/frame3b.png', 3)

    def onHoverIn(self, frame, tex=None, ring_id=None, event=None):
        if frame in self.ingore_hover:
            return
        if tex:
            frame['frameTexture']=loader.loadTexture(tex)
        frame['text_fg']=cfg['ui_color2']
        frame.setColor(cfg['ui_color2'])
        if ring_id is not None:
            self.rings[ring_id][0].setColor(cfg['ui_color2'])
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
        frame['text_fg']=cfg['ui_color1']
        frame.setColor(cfg['ui_color1'])
        if ring_id is not None:
            self.rings[ring_id][0].setColor(cfg['ui_color1'])
            LerpPosInterval(self.rings[ring_id][0], 0.2, (0,0, 0.0)).start()
            if self.rings[ring_id][2]:
                #self.rings[ring_id][2].getParticlesList()[0].renderer.setColor(cfg['ui_color1'])
                self.rings[ring_id][2].setColor(cfg['ui_color1'])
                self.rings[ring_id][2].setForce('up', 0)
                self.rings[ring_id][2].setForce('down', 1)

    def makeSmallButton(self, text, offset, cmd, parent):
        return self.makeButton(text, (256, 64), path+'gui/button.png', path+'gui/button.png', cmd, self.elements[parent], (-262,-self.canvas_size+offset), active_area=(200, 50, 54,9))

    def makeButton(self, text, size, tex, hover_tex, cmd, parent, offset, ring_id=None, font=None, active_area=None):
        if font is None:
            font=self.ui.font
        font_size=font.getPixelsPerUnit()
        if active_area:
            frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                    frameColor=(1,1,1,1.0),
                                    text=text,
                                    frameTexture=tex,
                                    text_scale=font_size,
                                    text_font=font,
                                    text_align=TextNode.ACenter,
                                    text_pos=(-size[0]/2+active_area[2]/2,size[1]/2-4),
                                    text_fg=cfg['ui_color1'],
                                    suppressMouse=0,
                                    parent=parent)
            _resetPivot(frame)
            frame.setPos(_pos2d(offset[0],offset[1]))
            frame.setColor(cfg['ui_color1'])
            frame.setTransparency(TransparencyAttrib.MAlpha)
            active_frame=DirectFrame(frameSize=_rec2d(active_area[0],active_area[1]),
                                    frameColor=(1,0,0,0.0),
                                    state=DGG.NORMAL,
                                    suppressMouse=0,
                                    parent=parent)
            _resetPivot(active_frame)
            active_frame.bind(DGG.WITHOUT, self.onHoverOut,[frame, tex, ring_id])
            active_frame.bind(DGG.WITHIN, self.onHoverIn, [frame, hover_tex, ring_id])
            active_frame.bind(DGG.B1PRESS, self.onCmd, [frame, cmd])
            active_frame.setPos(_pos2d(offset[0]+active_area[2],offset[1]+active_area[3]))
        else:
            frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                    frameColor=(1,1,1,1.0),
                                    text=text,
                                    frameTexture=tex,
                                    text_scale=font_size,
                                    text_font=font,
                                    text_align=TextNode.ACenter,
                                    text_pos=(-size[0]/2,size[1]/2-4),
                                    text_fg=cfg['ui_color1'],
                                    state=DGG.NORMAL,
                                    suppressMouse=0,
                                    parent=parent)
            _resetPivot(frame)
            frame.setPos(_pos2d(offset[0],offset[1]))
            frame.setColor(cfg['ui_color1'])
            frame.setTransparency(TransparencyAttrib.MAlpha)
            frame.bind(DGG.WITHOUT, self.onHoverOut,[frame, tex, ring_id])
            frame.bind(DGG.WITHIN, self.onHoverIn, [frame, hover_tex, ring_id])
            frame.bind(DGG.B1PRESS, self.onCmd, [frame, cmd])
        return frame

    def makeFrame(self, tex, parent, offset, size=(128, 128)):
        frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                frameColor=(1,1,1,1),
                                frameTexture=tex,
                                suppressMouse=0,
                                parent=parent)
        _resetPivot(frame)
        frame.setPos(_pos2d(offset[0],offset[1]))
        frame.setColor(cfg['ui_color1'])
        frame.setTransparency(TransparencyAttrib.MAlpha)
        return frame

    def _makeRing(self, tex_path, time, z):
        cm = CardMaker('plane')
        cm.setFrame(-30, 30, -30, 30)
        ring_plane=render.attachNewNode(cm.generate())
        tex=loader.loadTexture(tex_path)
        ring_plane.setTexture(tex)
        #ring_plane.setTransparency(TransparencyAttrib.MAlpha, 1)
        attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
        ring_plane.setAttrib(attrib)
        #ring_plane.setDepthOffset(4-z)
        #ring_plane.setBin('fixed', 20-z)
        ring_plane.setDepthTest(False)
        ring_plane.setDepthWrite(False)
        ring_plane.setPos(0,0,0)
        ring_plane.setHpr(0, -90, 0)
        ring_plane.setColor(cfg['ui_color1'])
        particle=Vfx('menu_ring', radius=12+z+(z*3), parent=ring_plane, color=cfg['ui_color1'] )
        interval=LerpHprInterval(ring_plane, time,(0, -90, 360))
        interval.loop()
        return (ring_plane, interval, particle)

