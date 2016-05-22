from direct.filter.FilterManager import FilterManager
from panda3d.core import *

class Filters():
    def __init__(self):
        self.filter_tex={}
        self.manager=FilterManager(base.win, base.cam)
        self.filters={}

        self.window_x=float(base.win.getXSize())
        self.window_y=float(base.win.getYSize())
        render.setShaderInput('screen_size',Vec2(self.window_x,self.window_y))
        log.debug('Filters: FilterManager started at '+str(base.win.getXSize())+'x'+str(base.win.getYSize()))

    def reset(self):
        self.manager.cleanup()
        self.filter_tex={}
        self.manager=FilterManager(base.win, base.cam)
        self.filters={}
        self.window_x=float(base.win.getXSize())
        self.window_y=float(base.win.getYSize())

    def setupFilters(self, useFxaa=True):
        colorTex = Texture()#the scene
        colorTex.setWrapU(Texture.WMClamp)
        colorTex.setWrapV(Texture.WMClamp)
        colorTex.setFormat(Texture.F_rgb16)
        auxTex = Texture() # r=blur, g=shadow, b=?, a=?
        composeTex=Texture()#the scene(colorTex) blured where auxTex.r>0 and with shadows (blurTex2.r) added
        self.filters={}
        final_quad = self.manager.renderSceneInto(colortex=colorTex, auxtex=auxTex)


        blurTex = Texture() #1/2 size of the shadows to be blured
        blurTex.setWrapU(Texture.WMClamp)
        blurTex.setWrapV(Texture.WMClamp)
        blurTex2 = Texture()
        blurTex2.setWrapU(Texture.WMClamp)
        blurTex2.setWrapV(Texture.WMClamp)
        glareTex = Texture()
        glareTex.setWrapU(Texture.WMClamp)
        glareTex.setWrapV(Texture.WMClamp)
        flareTex = Texture()
        flareTex.setWrapU(Texture.WMClamp)
        flareTex.setWrapV(Texture.WMClamp)
        flareTex2 = Texture()
        flareTex2.setWrapU(Texture.WMClamp)
        flareTex2.setWrapV(Texture.WMClamp)
        #blurr shadows #1
        interquad0 = self.manager.renderQuadInto(colortex=blurTex, div=8)
        interquad0.setShader(Shader.load(Shader.SLGLSL, path+'shaders/blur_v.glsl', path+'shaders/blur_f.glsl'))
        interquad0.setShaderInput('input_map', auxTex)
        interquad0.setShaderInput('sharpness', 0.008)
        self.filters['shadow']=interquad0
        #blurrscene
        interquad1 = self.manager.renderQuadInto(colortex=blurTex2, div=4)
        interquad1.setShader(Shader.load(Shader.SLGLSL, path+'shaders/blur_v.glsl', path+'shaders/blur_f.glsl'))
        interquad1.setShaderInput('input_map', colorTex)
        interquad1.setShaderInput('sharpness', 0.005)
        self.filters['blur']=interquad1
        #glare
        interquad2 = self.manager.renderQuadInto(colortex=glareTex, div=2)
        interquad2.setShader(Shader.load(Shader.SLGLSL, path+'shaders/glare_v.glsl', path+'shaders/glare_f.glsl'))
        interquad2.setShaderInput('auxTex', auxTex)
        interquad2.setShaderInput('colorTex', blurTex2)
        interquad2.setShaderInput('blurTex', blurTex)
        self.filters['glare']=interquad2
        #lense flare
        interquad3 = self.manager.renderQuadInto(colortex=flareTex, div=2)
        #interquad3.setShader(Shader.load(path+'shaders/lens_flare.sha'))
        #interquad3.setShaderInput('tex0', glareTex)
        interquad3.setShader(Shader.load(Shader.SLGLSL, path+'shaders/flare_v.glsl', path+'shaders/flare_f.glsl'))
        interquad3.setShaderInput('glareTex', glareTex)
        self.filters['flare']=interquad3
        interquad3a = self.manager.renderQuadInto(colortex=flareTex2, div=2)
        interquad3a.setShader(Shader.load(Shader.SLGLSL, path+'shaders/blur_v.glsl', path+'shaders/blur_f.glsl'))
        interquad3a.setShaderInput('input_map', flareTex)
        interquad3a.setShaderInput('sharpness', 0.005)
        self.filters['flare2']=interquad1
        if useFxaa:
            #compose the scene
            interquad4 = self.manager.renderQuadInto(colortex=composeTex)
            interquad4.setShader(Shader.load(Shader.SLGLSL, path+'shaders/compose_v.glsl', path+'shaders/compose_f.glsl'))
            interquad4.setShaderInput('flareTex', flareTex2)
            interquad4.setShaderInput('glareTex', glareTex)
            interquad4.setShaderInput('colorTex', colorTex)
            interquad4.setShaderInput('blurTex', blurTex)
            interquad4.setShaderInput('blurTex2', blurTex2)
            interquad4.setShaderInput('auxTex', auxTex)
            interquad4.setShaderInput('noiseTex', loader.loadTexture(path+'data/noise2.png'))
            star_tex=loader.loadTexture(path+'data/star.png')
            star_tex.setWrapU(Texture.WM_mirror_once)
            star_tex.setWrapV(Texture.WM_mirror_once)
            interquad4.setShaderInput('starTex', star_tex)
            interquad4.setShaderInput('time', 0.0)
            interquad4.setShaderInput('screen_size', Vec2(float(base.win.getXSize()),float(base.win.getYSize())))
            #fxaa
            final_quad.setShader(Shader.load(Shader.SLGLSL, path+'shaders/fxaa_v.glsl', path+'shaders/fxaa_f.glsl'))
            final_quad.setShaderInput('tex0', composeTex)
            final_quad.setShaderInput('rt_w',float(base.win.getXSize()))
            final_quad.setShaderInput('rt_h',float(base.win.getYSize()))
            final_quad.setShaderInput('FXAA_SPAN_MAX' , float(8.0))
            final_quad.setShaderInput('FXAA_REDUCE_MUL', float(1.0/8.0))
            final_quad.setShaderInput('FXAA_SUBPIX_SHIFT', float(1.0/4.0))
            self.filters['fxaa']=final_quad
            log.debug('Filters: Using post-process effects and FXAA')
        else:
            #compose the scene
            final_quad.setShader(Shader.load(Shader.SLGLSL, path+'shaders/compose_v.glsl', path+'shaders/compose_f.glsl'))
            final_quad.setShaderInput('flareTex', flareTex2)
            final_quad.setShaderInput('glareTex', glareTex)
            final_quad.setShaderInput('colorTex', colorTex)
            final_quad.setShaderInput('blurTex', blurTex)
            final_quad.setShaderInput('blurTex2', blurTex2)
            final_quad.setShaderInput('auxTex', auxTex)
            final_quad.setShaderInput('noiseTex', loader.loadTexture(path+'data/noise2.png'))
            star_tex=loader.loadTexture(path+'data/star.png')
            star_tex.setWrapU(Texture.WM_mirror_once)
            star_tex.setWrapV(Texture.WM_mirror_once)
            final_quad.setShaderInput('starTex', star_tex)
            final_quad.setShaderInput('time', 0.0)
            final_quad.setShaderInput('screen_size', Vec2(float(base.win.getXSize()),float(base.win.getYSize())))
            self.filters['compose']=final_quad
            log.debug('Filters: Using post-process effects without FXAA')

    def setupFxaa(self):
        colorTex = Texture()#the scene
        final_quad = self.manager.renderSceneInto(colortex=colorTex)
        final_quad.setShader(Shader.load(Shader.SLGLSL, path+'shaders/fxaa_v.glsl', path+'shaders/fxaa_f.glsl'))
        final_quad.setShaderInput('tex0', colorTex)
        final_quad.setShaderInput('rt_w',float(base.win.getXSize()))
        final_quad.setShaderInput('rt_h',float(base.win.getYSize()))
        final_quad.setShaderInput('FXAA_SPAN_MAX' , float(8.0))
        final_quad.setShaderInput('FXAA_REDUCE_MUL', float(1.0/8.0))
        final_quad.setShaderInput('FXAA_SUBPIX_SHIFT', float(1.0/4.0))
        self.filters['fxaa']=final_quad
        log.debug('Filters: Using FXAA only')

    def update(self):
        x=float(base.win.getXSize())
        y=float(base.win.getYSize())
        render.setShaderInput('screen_size',Vec2(x,y))
        if self.filters:
            if 'fxaa' in self.filters:
                self.filters['fxaa'].setShaderInput('rt_w',x)
                self.filters['fxaa'].setShaderInput('rt_h',y)
            if 'compose' in self.filters:
                self.filters['compose'].setShaderInput('screen_size',Vec2(x,y))
