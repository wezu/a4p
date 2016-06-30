from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.stdpy.file import listdir
import ast
import string
import re
import json
import traceback

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

class InGameMenu(DirectObject):
    """
    In Game Menu, the menu shown when you are in a match
    Beware! Blob/spaghetti code incoming!
    """
    def __init__(self, ui):
        self.ui=ui
        self.elements={}

        self.is_menu_hidden=True

        #crosshair
        self.elements['hud_crosshair']=DirectFrame(frameSize=_rec2d(64,64),
                                    frameColor=(1,1,1,1.0),
                                    frameTexture=loadTex(path+'gui/crosshair.png'),
                                    parent=self.ui.center)
        _resetPivot(self.elements['hud_crosshair'])
        self.elements['hud_crosshair'].setColor(cfg['ui_color1'])
        self.elements['hud_crosshair'].setTransparency(TransparencyAttrib.MAlpha)
        self.elements['hud_crosshair'].setPos(_pos2d(-32, -32))
        #orders menu
        self.elements['orders_attack']=self.makeOrdersButton(path+'gui/order1.png', (-128-64,-128), ' ', (-70,200))
        self.elements['orders_cover']=self.makeOrdersButton(path+'gui/order3.png', (-64,-128), '', (-60,200))
        self.elements['orders_defend']=self.makeOrdersButton(path+'gui/order2.png', (128-64,-128), ' ', (-50,200))

        self.elements['hud_health']=self.makeFrame('100', path+'gui/health.png', ui.bottom_left, (0,-64), (256,64), (-100, 12))
        #self.elements['hud_turbo']
        #self.elements['hud_weapon']
        #self.elements['hud_ammo']
        #self.elements['hud_money']
        #self.elements['hud_score']

        #set the shader for all elements except the scrolld frame/canvas
        self.setShader(path+'shaders/gui_v.glsl', path+'shaders/gui_f.glsl')

    def showElements(self, show_pattern):
        for  name, frame in self.elements.items():
            if name.startswith(show_pattern):
                frame.show()
            else:
                frame.hide()

    def showMenu(self, window_focus=None):
        if window_focus is not None:
            if window_focus == False and not self.ui.is_main_menu:
                if self.is_menu_hidden:
                    self.is_menu_hidden=False
                    self.hideCrosshair()
                    self.ui.showSoftCursor()
                    log.debug("showing menu")
            return
        if self.is_menu_hidden:
            self.is_menu_hidden=False
            self.hideCrosshair()
            self.ui.showSoftCursor()
            log.debug("showing menu")
        else:
            self.is_menu_hidden=True
            self.ui.hideSoftCursor()
            self.showElements('hud_')
            log.debug("hidding menu")

    def showOrders(self):
        if self.is_menu_hidden:
            self.is_menu_hidden=False
            self.ui.showSoftCursor()
            self.showElements('orders_')
            log.debug("showing orders")
        else:
            self.is_menu_hidden=True
            self.ui.hideSoftCursor()
            self.showElements('hud_')
            log.debug("hidding orders")

    def hide(self):
        for name, element in self.elements.items():
            element.hide()

    def show(self):
        for name, element in self.elements.items():
            if name != 'hud_crosshair':
                element.show()

    def showCrosshair(self):
        self.elements['hud_crosshair'].show()

    def hideCrosshair(self):
        self.elements['hud_crosshair'].hide()

    def setShader(self, v_shader, f_shader):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        for name, element in self.elements.items():
            element.setAttrib(shader_attrib)

    def makeFrame(self, txt, tex, parent, pos, size=(128, 128), text_pos=(0,0)):
        font=self.ui.font_special
        font_size=font.getPixelsPerUnit()
        frame=DirectFrame(frameSize=_rec2d(size[0],size[1]),
                                frameColor=(1,1,1,1),
                                frameTexture=loadTex(tex),
                                suppressMouse=0,
                                text=txt,
                                text_scale=font_size,
                                text_font=font,
                                text_align=TextNode.ACenter,
                                text_pos=text_pos,
                                text_fg=cfg['ui_color2'],
                                parent=parent)
        _resetPivot(frame)
        frame.setPos(_pos2d(pos[0],pos[1]))
        frame.setColor(cfg['ui_color1'])
        frame.setTransparency(TransparencyAttrib.MAlpha)
        return frame

    def makeOrdersButton(self, tex, pos, txt, txt_pos):
        font=self.ui.font
        font_size=font.getPixelsPerUnit()
        frame=DirectFrame(frameSize=_rec2d(128,256),
                                    frameColor=(1,1,1,1.0),
                                    text=txt,
                                    frameTexture=loadTex(tex),
                                    text_scale=font_size,
                                    text_font=font,
                                    text_align=TextNode.ACenter,
                                    text_pos=txt_pos,
                                    text_fg=cfg['ui_color2'],
                                    state=DGG.NORMAL,
                                    suppressMouse=True,
                                    parent=self.ui.center)
        _resetPivot(frame)
        frame.setPos(_pos2d(pos[0],pos[1]))
        frame.setColor(cfg['ui_color1'])
        frame.setTransparency(TransparencyAttrib.MAlpha)
        frame.hide()
        return frame
