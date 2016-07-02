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
        if cfg['use-filters']:
            self.setupFilters()
        elif cfg['use-fxaa']:
            self.setupFxaa()

    def reset(self):
        self.manager.cleanup()
        self.filter_tex={}
        self.manager=FilterManager(base.win, base.cam)
        self.filters={}
        self.window_x=float(base.win.getXSize())
        self.window_y=float(base.win.getYSize())
        if cfg['glsl-blur'] or cfg['glsl-distortion'] or cfg['glsl-flare'] or cfg['glsl-glare'] or cfg['glsl-lut']:
            self.setupFilters()
        elif cfg['use-fxaa']:
            self.setupFxaa()

    def setupFilters(self):
        colorTex = Texture()#the scene
        colorTex.setWrapU(Texture.WMClamp)
        colorTex.setWrapV(Texture.WMClamp)

        auxTex = Texture()
        auxTex.setWrapU(Texture.WMClamp)
        auxTex.setWrapV(Texture.WMClamp)

        composeTex = Texture()
        composeTex.setWrapU(Texture.WMClamp)
        composeTex.setWrapV(Texture.WMClamp)

        self.filters={}
        final_quad = self.manager.renderSceneInto(colortex=colorTex, auxtex=auxTex)

        if cfg['glsl-blur'] or cfg['glsl-distortion'] or cfg['glsl-glare'] or cfg['glsl-flare']:
            if cfg['glsl-blur']:
                #blur scene
                blurTex = Texture()
                blurTex.setWrapU(Texture.WMClamp)
                blurTex.setWrapV(Texture.WMClamp)
                interquad0 = self.manager.renderQuadInto(colortex=blurTex, div=2)
                interquad0.setShader(Shader.load(Shader.SLGLSL, path+'shaders/blur_v.glsl', path+'shaders/blur_f.glsl'))
                interquad0.setShaderInput('input_map', colorTex)
                interquad0.setShaderInput('sharpness', 0.008)
                self.filters['blur']=interquad0
            if cfg['glsl-flare'] or cfg['glsl-glare']:
                #blur aux
                blurTex2 = Texture()
                blurTex2.setWrapU(Texture.WMClamp)
                blurTex2.setWrapV(Texture.WMClamp)
                interquad0 = self.manager.renderQuadInto(colortex=blurTex2, div=2)
                interquad0.setShader(Shader.load(Shader.SLGLSL, path+'shaders/blur_ex_v.glsl', path+'shaders/blur_ex_f.glsl'))
                interquad0.setShaderInput('input_map', auxTex)
                #interquad0.setShaderInput('sharpness', 0.02)
                self.filters['blur_aux']=interquad0

                #glare
                glareTex = Texture()
                glareTex.setWrapU(Texture.WMClamp)
                glareTex.setWrapV(Texture.WMClamp)
                interquad2 = self.manager.renderQuadInto(colortex=glareTex)
                interquad2.setShader(Shader.load(Shader.SLGLSL, path+'shaders/glare_v.glsl', path+'shaders/glare_f.glsl'))
                interquad2.setShaderInput('auxTex', auxTex)
                interquad2.setShaderInput('colorTex', colorTex)
                interquad2.setShaderInput('blurAuxTex', blurTex2)
                self.filters['glare']=interquad2
            if cfg['glsl-flare']:
                #flare
                flareTex = Texture()
                flareTex.setWrapU(Texture.WMClamp)
                flareTex.setWrapV(Texture.WMClamp)
                flareTex2 = Texture()
                flareTex2.setWrapU(Texture.WMClamp)
                flareTex2.setWrapV(Texture.WMClamp)
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
                interquad3a.setShaderInput('sharpness', 0.008)
                self.filters['flare2']=interquad3a

        if cfg['use-fxaa']:
            #compose the scene
            interquad4 = self.manager.renderQuadInto(colortex=composeTex)
            interquad4.setShader(Shader.load(Shader.SLGLSL, path+'shaders/compose_v.glsl', path+'shaders/compose_f.glsl'))
            interquad4.setShaderInput('colorTex', colorTex)
            interquad4.setShaderInput('auxTex', auxTex)
            if cfg['glsl-blur']:
                dof_tex=loader.loadTexture(path+'data/dof.png')
                dof_tex.setWrapU(Texture.WM_mirror_once)
                dof_tex.setWrapV(Texture.WM_mirror_once)
                interquad4.setShaderInput('dofTex', dof_tex)
                interquad4.setShaderInput('blurTex', blurTex)
            if cfg['glsl-glare']:
                interquad4.setShaderInput('glareTex', glareTex)
            if cfg['glsl-flare']:
                interquad4.setShaderInput('flareTex', flareTex2)
                star_tex=loader.loadTexture(path+'data/'+cfg['flare-tex'])
                star_tex.setWrapU(Texture.WM_mirror_once)
                star_tex.setWrapV(Texture.WM_mirror_once)
                interquad4.setShaderInput('starTex', star_tex)
            if cfg['glsl-lut']:
                lut_tex=loader.loadTexture(path+'data/'+cfg['lut-tex'])
                lut_tex.setFormat(Texture.F_rgb16)
                lut_tex.setWrapU(Texture.WMClamp)
                lut_tex.setWrapV(Texture.WMClamp)
                interquad4.setShaderInput('lut', lut_tex)
            interquad4.setShaderInput('screen_size', Vec2(float(base.win.getXSize()),float(base.win.getYSize())))
            self.filters['compose']=interquad4

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
            final_quad.setShader(Shader.load(Shader.SLGLSL, path+'shaders/compose_v.glsl', path+'shaders/compose_f.glsl'))
            final_quad.setShaderInput('colorTex', colorTex)
            final_quad.setShaderInput('auxTex', auxTex)
            if cfg['glsl-blur']:
                dof_tex=loader.loadTexture(path+'data/dof.png')
                dof_tex.setWrapU(Texture.WM_mirror_once)
                dof_tex.setWrapV(Texture.WM_mirror_once)
                final_quad.setShaderInput('dofTex', dof_tex)
                final_quad.setShaderInput('blurTex', blurTex)
            if cfg['glsl-glare']:
                final_quad.setShaderInput('glareTex', glareTex)
            if cfg['glsl-flare']:
                final_quad.setShaderInput('flareTex', flareTex2)
                star_tex=loader.loadTexture(path+'data/star.png')
                star_tex.setWrapU(Texture.WM_mirror_once)
                star_tex.setWrapV(Texture.WM_mirror_once)
                final_quad.setShaderInput('starTex', star_tex)
            if cfg['glsl-lut']:
                lut_tex=loader.loadTexture(path+'data/'+cfg['lut-tex'])
                lut_tex.setFormat(Texture.F_rgb16)
                lut_tex.setWrapU(Texture.WMClamp)
                lut_tex.setWrapV(Texture.WMClamp)
                final_quad.setShaderInput('lut', lut_tex)
            final_quad.setShaderInput('screen_size', Vec2(float(base.win.getXSize()),float(base.win.getYSize())))

            self.filters['compose']=final_quad
            log.debug('Filters: Using post-process effects without FXAA')

        for buff in self.manager.buffers:
            buff.setClearValue(GraphicsOutput.RTPAuxRgba0, (0.0, 0.0, 0.0, 1.0))

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

    def reloadShaders(self):
        for name, quad in self.filters.items():
            shader=quad.getShader()
            v_shader=shader.getFilename(Shader.ST_vertex)
            f_shader=shader.getFilename(Shader.ST_fragment)
            quad.setShader(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        self.update()

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
