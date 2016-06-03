from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.stdpy.file import listdir
import ast
import string
import re

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

def loadTex(texturePath, wrap=SamplerState.WM_mirror, srgb=None):
    tex=loader.loadTexture(texturePath)
    tex.setWrapU(wrap)
    tex.setWrapV(wrap)
    tex.setWrapW(wrap)
    if srgb is None: #None == Auto, whatever the cfg says
        srgb=cfg['srgb']
    if srgb:
        tex_format=tex.getFormat()
        if tex_format==Texture.F_rgb:
            tex_format=Texture.F_srgb
        elif tex_format==Texture.F_rgba or Texture.F_rgbm:
            tex_format=Texture.F_srgb_alpha
        tex.setFormat(tex_format)
    return tex

class MainMenu(DirectObject):
    """
    Main Menu, the menu shown before starting a match or between them
    Beware! Blob/spaghetti code incoming!
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
        self.elements['fixed_frame_top_left']=self.makeFrame(path+'gui/corner_left_up.png', ui.top_left, (0,0))
        self.elements['fixed_frame_top_right']=self.makeFrame(path+'gui/corner_right_up.png', ui.top_right, (-128,0))
        self.elements['fixed_frame_bottom_left']=self.makeFrame(path+'gui/corner_left_down.png', ui.bottom_left, (0,-128))
        self.elements['fixed_frame_bottom_right']=self.makeFrame(path+'gui/corner_right_down.png', ui.bottom_right, (-128,-128))

        #close button
        self.elements['fixed_close_button']=self.makeButton('', (64, 64), path+'gui/empty_64.png', path+'gui/close.png', self.onExit, ui.top_right, (-64,0), 4)
        #tutorial button
        self.elements['fixed_tutorial_button']=self.makeButton('TUTORIAL', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showTutorialMenu, ui.top_left, (0,0), 2, ui.font_special )
        #host button
        self.elements['fixed_host_button']=self.makeButton('HOST', (256, 128), path+'gui/frame2b.png', path+'gui/frame2b.png', self.showHostMenu, ui.top, (-128,0), 0, ui.font_special )
        #join button
        self.elements['fixed_join_button']=self.makeButton('JOIN', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showJoinMenu, ui.top, (-128,128), 1, ui.font_special )
        #options
        self.elements['fixed_option_button']=self.makeButton('OPTIONS', (256, 128), path+'gui/frame3b.png', path+'gui/frame3b.png', self.showOptionMenu, ui.top_left, (0,128), 3, ui.font_special )

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
        self.last_config_val=None
        self.last_config_name=None
        self.last_focused_entry=None
        self.last_entry_config_name=None

        #we make a big canvas for all the buttons to fit, so we don't need to resize the canvas later
        #minimal canvas size is 15*64 (number of buttons * button size)
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
                                                            verticalScroll_frameTexture=loadTex(path+'gui/line2.png'),
                                                            verticalScroll_relief=DGG.FLAT,
                                                            verticalScroll_resizeThumb=False,
                                                            verticalScroll_thumb_relief=DGG.FLAT,
                                                            verticalScroll_thumb_frameSize=_rec2d(16,64),
                                                            verticalScroll_thumb_frameColor=cfg['ui_color1'],
                                                            verticalScroll_thumb_frameTexture=loadTex(path+'gui/thumb.png')
                                                            )
        _resetPivot(self.elements['scrolled_frame'])
        self.elements['scrolled_frame'].setPos(_pos2d(0,-48))
        self.elements['scrolled_frame'].setTransparency(TransparencyAttrib.MAlpha)
        self.elements['scrolled_frame'].hide()
        self.elements['scrolled_frame'].verticalScroll.incButton.hide()
        self.elements['scrolled_frame'].verticalScroll.decButton.hide()
        self.elements['fixed_scroll_canvas']=self.elements['scrolled_frame'].getCanvas()
        #all the options buttons
        self.elements['options_res']=self.makeSmallButton('Resolution', 0, self.showResSelect, 'fixed_scroll_canvas')
        self.elements['options_audio']=self.makeSmallButton('Audio', 64, self.showVolumeSelece, 'fixed_scroll_canvas')
        self.elements['options_shadows']=self.makeSmallButton('Shadows', 64*2, self.showOptionMenu, 'fixed_scroll_canvas')
        self.elements['options_filters']=self.makeSmallButton('Special Effects', 64*3, self.showOptionMenu, 'fixed_scroll_canvas')
        self.elements['options_mouse']=self.makeSmallButton('Mouse speed', 64*4, self.showOptionMenu, 'fixed_scroll_canvas')
        self.elements['options_key_forward']=self.makeSmallButton('KEY: forward', 64*5, self.showKeyBind, 'fixed_scroll_canvas', arg='forward')
        self.elements['options_key_back']=self.makeSmallButton('KEY: back', 64*6, self.showKeyBind, 'fixed_scroll_canvas', arg='back')
        self.elements['options_key_left']=self.makeSmallButton('KEY: left', 64*7, self.showKeyBind, 'fixed_scroll_canvas', arg='left')
        self.elements['options_key_right']=self.makeSmallButton('KEY: right', 64*8, self.showKeyBind, 'fixed_scroll_canvas', arg='right')
        self.elements['options_key_fire']=self.makeSmallButton('KEY: fire', 64*9, self.showKeyBind, 'fixed_scroll_canvas', arg='fire')
        self.elements['options_key_zoom']=self.makeSmallButton('KEY: zoom', 64*10, self.showKeyBind, 'fixed_scroll_canvas', arg='zoom')
        self.elements['options_key_sprint']=self.makeSmallButton('KEY: sprint', 64*11, self.showKeyBind, 'fixed_scroll_canvas', arg='sprint')
        self.elements['options_key_sprint']=self.makeSmallButton('KEY: orders', 64*12, self.showKeyBind, 'fixed_scroll_canvas', arg='orders')
        self.elements['options_key_menu']=self.makeSmallButton('KEY: show  menu', 64*13, self.showKeyBind, 'fixed_scroll_canvas', arg='menu')

        #levels
        for i, level in enumerate(self.known_levels):
            self.elements['level_'+level]=self.makeSmallButton(level, 64*i, self.showOptionMenu, 'fixed_scroll_canvas')
            #self.elements['level_'+level].hide()


        #key-binding
        base.buttonThrowers[0].node().setButtonDownEvent('button-down')
        #self.accept('button-down', self.getKey)
        self.elements['key_bind_text']=self.makeTxt('alpha beta\ngamma', self.elements['tooltip_frame'], (128,-70))
        self.elements['key_bind_key_name']=self.makeTxt('???', self.elements['tooltip_frame'], (128,-140))
        self.elements['save_cfg']=self.makeButton('SAVE', (256, 128), path+'gui/button3.png', path+'gui/button3.png', self.saveConfig, self.elements['tooltip_frame'], (0,128), active_area=(212, 70, 12, 47), arg=None, suppress=1)
        self.elements['save_cfg']['text_pos']=(120, -84)
        self.elements['key_bind_key_name']['fg']=cfg['ui_color2']

        #resolution
        self.elements['res_text']=self.makeTxt('Width, Height:\n\n\nFullscreen:', self.elements['tooltip_frame'], (128,-70))
        self.elements['res_text'].setPos(128, -48)
        #DirectEntry hell...
        self.elements['res_entry']=DirectEntry(text = "800,600",
                                            initialText="800,600",
                                            text_font=ui.font,
                                            frameSize=_rec2d(256,64),
                                            frameColor=(1,1,1,1.0),
                                            frameTexture=loadTex(path+'gui\entry.png'),
                                            text_scale=ui.font.getPixelsPerUnit(),
                                            text_pos=(-180,30),
                                            focus=0,
                                            state=DGG.NORMAL,
                                            text_fg=cfg['ui_color1'],
                                            command=self.setConfigFromEntry,
                                            focusInCommand=self.setConfigFromEntry,
                                            focusOutCommand=self.setConfigFromEntry,
                                            focusInExtraArgs=[None, 'res_entry', 'win-size'],
                                            focusOutExtraArgs=[None, 'res_entry', 'win-size'],
                                            extraArgs=['res_entry', 'fullscreen'],
                                            parent=self.elements['tooltip_frame'])
        self.elements['res_entry'].setPos(270, 0, -106)
        self.elements['res_entry'].guiItem.setBlinkRate(2.0)
        self.elements['res_entry'].guiItem.getCursorDef().setColor(cfg['ui_color1'], 1)
        self.elements['res_entry'].bind(DGG.B1PRESS, self.setEntryCursorPos, [self.elements['res_entry']])
        self.elements['fullscreen_entry']=DirectEntry(text = "0",
                                            initialText="0",
                                            text_font=ui.font,
                                            frameSize=_rec2d(256,64),
                                            frameColor=(1,1,1,1.0),
                                            frameTexture=loadTex(path+'gui\entry.png'),
                                            text_scale=ui.font.getPixelsPerUnit(),
                                            text_pos=(-180,30),
                                            focus=0,
                                            state=DGG.NORMAL,
                                            text_fg=cfg['ui_color1'],
                                            command=self.setConfigFromEntry,
                                            focusInCommand=self.setConfigFromEntry,
                                            focusOutCommand=self.setConfigFromEntry,
                                            focusInExtraArgs=[None, 'fullscreen_entry', 'fullscreen'],
                                            focusOutExtraArgs=[None, 'fullscreen_entry', 'fullscreen'],
                                            extraArgs=['fullscreen_entry', 'fullscreen'],
                                            parent=self.elements['tooltip_frame'])
        self.elements['fullscreen_entry'].setPos(270, 0, -170)
        self.elements['fullscreen_entry'].guiItem.setBlinkRate(2.0)
        self.elements['fullscreen_entry'].guiItem.getCursorDef().setColor(cfg['ui_color1'], 1)
        self.elements['fullscreen_entry'].bind(DGG.B1PRESS, self.setEntryCursorPos, [self.elements['fullscreen_entry']])

        #audio (sound and music volume)
        self.elements['audio_text']=self.makeTxt('Music Volume:\n\n\nSound Volume:', self.elements['tooltip_frame'], (128,-70))
        self.elements['audio_text'].setPos(128, -48)
        #DirectEntry hell...
        self.elements['music_entry']=DirectEntry(text = "1.0",
                                            initialText="1.0",
                                            text_font=ui.font,
                                            frameSize=_rec2d(256,64),
                                            frameColor=(1,1,1,1.0),
                                            frameTexture=loadTex(path+'gui\entry.png'),
                                            text_scale=ui.font.getPixelsPerUnit(),
                                            text_pos=(-180,30),
                                            focus=0,
                                            state=DGG.NORMAL,
                                            text_fg=cfg['ui_color1'],
                                            command=self.setConfigFromEntry,
                                            focusInCommand=self.setConfigFromEntry,
                                            focusOutCommand=self.setConfigFromEntry,
                                            focusInExtraArgs=[None, 'music_entry', 'music-volume'],
                                            focusOutExtraArgs=[None, 'music_entry', 'music-volume'],
                                            extraArgs=['music_entry', 'music-volume'],
                                            parent=self.elements['tooltip_frame'])
        self.elements['music_entry'].setPos(270, 0, -106)
        self.elements['music_entry'].guiItem.setBlinkRate(2.0)
        self.elements['music_entry'].guiItem.getCursorDef().setColor(cfg['ui_color1'], 1)
        self.elements['music_entry'].bind(DGG.B1PRESS, self.setEntryCursorPos, [self.elements['music_entry']])
        self.elements['sound_entry']=DirectEntry(text = "1.0",
                                            initialText="1.0",
                                            text_font=ui.font,
                                            frameSize=_rec2d(256,64),
                                            frameColor=(1,1,1,1.0),
                                            frameTexture=loadTex(path+'gui\entry.png'),
                                            text_scale=ui.font.getPixelsPerUnit(),
                                            text_pos=(-180,30),
                                            focus=0,
                                            state=DGG.NORMAL,
                                            text_fg=cfg['ui_color1'],
                                            command=self.setConfigFromEntry,
                                            focusInCommand=self.setConfigFromEntry,
                                            focusOutCommand=self.setConfigFromEntry,
                                            focusInExtraArgs=[None, 'sound_entry', 'sound-volume'],
                                            focusOutExtraArgs=[None, 'sound_entry', 'sound-volume'],
                                            extraArgs=['sound_entry', 'sound-volume'],
                                            parent=self.elements['tooltip_frame'])
        self.elements['sound_entry'].setPos(270, 0, -170)
        self.elements['sound_entry'].guiItem.setBlinkRate(2.0)
        self.elements['sound_entry'].guiItem.getCursorDef().setColor(cfg['ui_color1'], 1)
        self.elements['sound_entry'].bind(DGG.B1PRESS, self.setEntryCursorPos, [self.elements['sound_entry']])

        #mouse wheel handling
        self.accept('wheel_up', self.scroll, [-1])
        self.accept('wheel_down', self.scroll, [1])

        #set the shader for all elements except the scrolld frame/canvas
        self.setShader(path+'shaders/gui_v.glsl', path+'shaders/gui_f.glsl')

    def setConfigFromEntry(self, text, entry, name, event=None):
        if name is None:
            return
        self.last_focused_entry=entry
        self.last_entry_config_name=name
        if text is None:
            text=self.elements[entry].get()
        if text in ('true', 'True', '#t', 'yes'):
            val=1
        elif text in ('false', 'False', '#f', 'no'):
            val=0
        else:
            allow = string.digits + '., '
            text=re.sub('[^%s]' % allow, '', text)
            try:
                val=ast.literal_eval(text)
            except:
                try:
                    val=[]
                    for txt in text.split():
                        val.append(ast.literal_eval(txt))
                except:
                    return
        if self.last_config_name is None:
            self.last_config_name=name
            self.last_config_val=val
        elif isinstance(self.last_config_name, basestring):
            if self.last_config_name==name:
                self.last_config_val=val
            else:
                self.last_config_name=[self.last_config_name]
                self.last_config_name.append(name)
                self.last_config_val=[self.last_config_val]
                self.last_config_val.append(val)
        elif name in self.last_config_name:
            id=self.last_config_name.index(name)
            self.last_config_val[id]=val
        else:
            self.last_config_name.append(name)
            self.last_config_val.append(val)

    def setEntryCursorPos(self, entry, event):
        #print entry.guiItem.getCursorPosition()
        #print event.getMouse()
        m=event.getMouse()
        pixel_pos=entry.getRelativePoint(render2d, Point3(m[0], 0, m[1]))
        new_cursor_pos= max(0, min(int(pixel_pos[0])+189, 125))/11
        entry.guiItem.setCursorPosition(new_cursor_pos)
        #print self.ui.cursor.getPos(pixel2d)

    def showVolumeSelece(self):
        self.last_config_val=None
        self.last_config_name=None
        self.elements['music_entry'].set(str(cfg['music-volume']))
        self.elements['sound_entry'].set(str(cfg['sound-volume']))
        self.last_config_val=None
        self.last_config_name=None
        self.showElements('options_')
        self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar2.png')
        self.fadeIn(self.elements['tooltip_frame'], cfg['ui_color3'])
        self.fadeIn(self.elements['save_cfg'], cfg['ui_color1'])
        self.elements['music_entry'].show()
        self.elements['sound_entry'].show()
        self.elements['audio_text'].show()

    def showResSelect(self):
        self.elements['res_entry'].set(str(base.win.getXSize())+', '+str(base.win.getYSize()))
        self.last_config_val=None
        self.last_config_name=None
        self.showElements('options_')
        self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar2.png')
        self.fadeIn(self.elements['tooltip_frame'], cfg['ui_color3'])
        self.elements['res_text'].show()
        self.fadeIn(self.elements['save_cfg'], cfg['ui_color1'])
        self.elements['res_entry'].show()
        self.elements['fullscreen_entry'].show()

    def saveConfig(self):
        self.setConfigFromEntry(None,self.last_focused_entry,self.last_entry_config_name)
        if self.last_config_val:
            if isinstance(self.last_config_name, basestring):
                cfg[self.last_config_name]=self.last_config_val
            else:
                for name, value in zip(self.last_config_name, self.last_config_val):
                    cfg[name]=value
            cfg.saveConfig(path+'config.txt')

        self.elements['tooltip_frame'].hide()
        self.elements['save_cfg'].hide()
        self.elements['key_bind_text'].hide()
        self.elements['key_bind_key_name'].hide()

    def getKey(self, keyname):
        self.last_config_val=keyname
        self.elements['key_bind_key_name']['text']=keyname

    def showKeyBind(self, key):
        self.showElements('options_')
        self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar2.png')
        self.last_config_name='key-'+key
        self.fadeIn(self.elements['tooltip_frame'], cfg['ui_color3'])
        self.fadeIn(self.elements['save_cfg'], cfg['ui_color1'])
        self.elements['key_bind_text'].show()
        self.elements['key_bind_key_name'].show()
        self.elements['key_bind_text']['text']='Press key for:\n'+key.upper()+'\nCurrent key is:\n\n'
        #self.accept('button-down', self.getKey)
        Sequence(Wait(0.1), Func(self.accept, 'button-down', self.getKey)).start()
        self.elements['key_bind_key_name']['text']=cfg['key-'+key]


    def scroll(self, direction):
        v=self.elements['scrolled_frame'].verticalScroll['value']
        self.elements['scrolled_frame'].verticalScroll['value']=v+direction*cfg['mouse-scroll-speed']

    def setShader(self, v_shader, f_shader):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        for name, element in self.elements.iteritems():
            if name not in ('scrolled_frame'):
                element.setAttrib(shader_attrib)
        self.elements['scrolled_frame'].verticalScroll.setAttrib(shader_attrib)
        self.elements['scrolled_frame'].verticalScroll.thumb.setAttrib(shader_attrib)

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
        self.elements[bar]['frameTexture']=loadTex(path+tex)
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
        if main_button=='fixed_tutorial_button':
            self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar1.png')
            self.showElements('level_','options_')
        if main_button=='fixed_host_button':
            self.showContentFrame(line='link_line_2', bar='link_bar_2', tex='gui/bar1.png')
            self.showElements('level_','options_')
        if main_button=='fixed_join_button':
            self.showContentFrame(line='link_line_2', bar='link_bar_2', tex='gui/bar2.png')
            self.showElements('hosts_',('options_','level_'))
        if main_button=='fixed_option_button':
            self.showElements('options_')
            self.showContentFrame(line='link_line_1', bar='link_bar_1', tex='gui/bar2.png')
        for element in self.last_element_list:
            self.elements[element].hide()
        for element in element_list:
            self.fadeIn(self.elements[element],cfg['ui_color3'])

        self.ingore_hover.append(self.elements[main_button])
        self.last_element_list=element_list

    def showElements(self, show_pattern, color=cfg['ui_color1']):
        for  name, frame in self.elements.iteritems():
            if name.startswith('fixed_'):
                pass
            elif name.startswith(show_pattern):
                self.fadeIn(frame, color)
            else:
                frame.hide()

    def showTutorialMenu(self):
        self.showMenu('fixed_tutorial_button', 2, [])

    def showOptionMenu(self):
        self.showMenu('fixed_option_button', 3, [])

    def showHostMenu(self):
        self.showMenu('fixed_host_button', 0, [])

    def showJoinMenu(self):
        self.showMenu('fixed_join_button', 1, [])

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
        self.elements['res_entry'].set(str(window_x)+', '+str(window_y))

    def hide(self):
        for element in self.elements.itervalues():
            element.hide()
        for ring in self.rings:
            ring[0].hide()
            ring[1].pause()
            ring[2].hide()

    def show(self):
        self.elements['fixed_close_button'].show()
        self.elements['fixed_tutorial_button'].show()
        self.elements['fixed_host_button'].show()
        self.elements['fixed_join_button'].show()
        self.elements['fixed_option_button'].show()
        self.elements['fixed_frame_top_left'].show()
        self.elements['fixed_frame_top_right'].show()
        self.elements['fixed_frame_bottom_left'].show()
        self.elements['fixed_frame_bottom_right'].show()
        for ring in self.rings:
            ring[0].show()
            ring[1].loop()
            ring[2].show()

    def onExit(self):
        messenger.send('exit-event')

    def onCmd(self, frame, cmd, arg=[], event=None):
        self.ignore('button-down')
        messenger.send('audio-sfx',['click'])
        if arg:
            cmd(arg)
        else:
            cmd()

    def hoverAllOut(self):
        self.onHoverOut(self.elements['fixed_close_button'], path+'gui/empty_64.png', 4)
        self.onHoverOut(self.elements['fixed_tutorial_button'], path+'gui/frame2b.png', 2)
        self.onHoverOut(self.elements['fixed_host_button'], path+'gui/frame2b.png', 0)
        self.onHoverOut(self.elements['fixed_join_button'], path+'gui/frame3b.png', 1)
        self.onHoverOut(self.elements['fixed_option_button'], path+'gui/frame3b.png', 3)

    def onHoverIn(self, frame, tex=None, ring_id=None, event=None):
        if frame in self.ingore_hover:
            return
        if tex:
            frame['frameTexture']=loadTex(tex)
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
            frame['frameTexture']=loadTex(tex)
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

    def makeSmallButton(self, text, offset, cmd, parent, arg=[]):
        return self.makeButton(text, (256, 64), path+'gui/button.png', path+'gui/button.png', cmd, self.elements[parent], (-262,-self.canvas_size+offset), active_area=(200, 50, 54,9), arg=arg)

    def makeButton(self, text, size, tex, hover_tex, cmd, parent, offset, ring_id=None, font=None, active_area=None, arg=[], suppress=0):
        if font is None:
            font=self.ui.font
        font_size=font.getPixelsPerUnit()
        if active_area:
            frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                    frameColor=(1,1,1,1.0),
                                    text=text,
                                    frameTexture=loadTex(tex),
                                    text_scale=font_size,
                                    text_font=font,
                                    text_align=TextNode.ACenter,
                                    text_pos=(-size[0]/2+active_area[2]/2,size[1]/2-4),
                                    text_fg=cfg['ui_color1'],
                                    suppressMouse=suppress,
                                    parent=parent)
            _resetPivot(frame)
            frame.setPos(_pos2d(offset[0],offset[1]))
            frame.setColor(cfg['ui_color1'])
            frame.setTransparency(TransparencyAttrib.MAlpha)
            active_frame=DirectFrame(frameSize=_rec2d(active_area[0],active_area[1]),
                                    frameColor=(1,0,0,0.0),
                                    frameTexture=loadTex(path+'gui/empty_64.png'),
                                    state=DGG.NORMAL,
                                    suppressMouse=suppress,
                                    parent=parent)
            _resetPivot(active_frame)
            active_frame.bind(DGG.WITHOUT, self.onHoverOut,[frame, tex, ring_id])
            active_frame.bind(DGG.WITHIN, self.onHoverIn, [frame, hover_tex, ring_id])
            active_frame.bind(DGG.B1PRESS, self.onCmd, [frame, cmd, arg])
            active_frame.setPos(_pos2d(offset[0]+active_area[2],offset[1]+active_area[3]))
            active_frame.wrtReparentTo(frame)
        else:
            frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                    frameColor=(1,1,1,1.0),
                                    text=text,
                                    frameTexture=loadTex(tex),
                                    text_scale=font_size,
                                    text_font=font,
                                    text_align=TextNode.ACenter,
                                    text_pos=(-size[0]/2,size[1]/2-4),
                                    text_fg=cfg['ui_color1'],
                                    state=DGG.NORMAL,
                                    suppressMouse=suppress,
                                    parent=parent)
            _resetPivot(frame)
            frame.setPos(_pos2d(offset[0],offset[1]))
            frame.setColor(cfg['ui_color1'])
            frame.setTransparency(TransparencyAttrib.MAlpha)
            frame.bind(DGG.WITHOUT, self.onHoverOut,[frame, tex, ring_id])
            frame.bind(DGG.WITHIN, self.onHoverIn, [frame, hover_tex, ring_id])
            frame.bind(DGG.B1PRESS, self.onCmd, [frame, cmd, arg])
        return frame

    def makeTxt(self, text, parent, offset, font=None):
        if font is None:
            font=self.ui.font
        font_size=font.getPixelsPerUnit()
        frame=OnscreenText(text=text,
                                scale=font_size,
                                font=font,
                                align=TextNode.ACenter,
                                fg=cfg['ui_color1'],
                                parent=parent)
        frame.setPos(offset[0],offset[1])
        return frame

    def makeFrame(self, tex, parent, offset, size=(128, 128)):
        frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                frameColor=(1,1,1,1),
                                frameTexture=loadTex(tex),
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
        tex=loadTex(tex_path)
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

