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

        self.elements['crosshair']=DirectFrame(frameSize=_rec2d(64,64),
                                    frameColor=(1,1,1,1.0),
                                    frameTexture=loadTex(path+'gui/crosshair.png'),
                                    parent=self.ui.center)
        _resetPivot(self.elements['crosshair'])
        self.elements['crosshair'].setColor(cfg['ui_color1'])
        self.elements['crosshair'].setTransparency(TransparencyAttrib.MAlpha)
        self.elements['crosshair'].setPos(_pos2d(-32, -32))

        #set the shader for all elements except the scrolld frame/canvas
        self.setShader(path+'shaders/gui_v.glsl', path+'shaders/gui_f.glsl')

    def hide(self):
        for name, element in self.elements.iteritems():
            element.hide()

    def show(self):
        for name, element in self.elements.iteritems():
            if name != 'crosshair':
                element.show()

    def showCrosshair(self):
        self.elements['crosshair'].show()

    def hideCrosshair(self):
        self.elements['crosshair'].hide()

    def setShader(self, v_shader, f_shader):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        for name, element in self.elements.iteritems():
            element.setAttrib(shader_attrib)
