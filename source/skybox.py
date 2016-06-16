from panda3d.core import *

class Skybox():
    def __init__(self, light_manager):
        self.lights=light_manager
        self.clock=0.0
        self.skyimg=PNMImage(path+'data/sky_grad.png')
        self.fog_color=(0, 0, 0, 1)
        self.sun_color=(1, 1, 1, 1)
        self.sky_color=(0, 0, 1, 1)
        self.cloud_color=(1, 1, 1, 1)
        self.skydome=loader.loadModel(path+'data/skydome')
        self.skydome.setPos(0, 0, -50)
        self.skydome.setScale(3)
        render.setShaderInput("cloudTile",8.0)
        render.setShaderInput("cloudSpeed",0.01)
        self.skydome.setBin('background', 1)
        #self.skydome.setTwoSided(True)
        self.skydome.node().setBounds(OmniBoundingVolume())
        self.skydome.node().setFinal(1)
        self.skydome.setTransparency(TransparencyAttrib.MNone, 1)
        self.skydome.setShader(Shader.load(Shader.SLGLSL, path+'shaders/sky_v.glsl',path+'shaders/sky_f.glsl'))
        self.skydome.reparentTo(render)
        self.skydome.hide()

    def show(self):
        self.skydome.show()

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
        self.sun_color=self.blendPixels(p1, p2, blend)
        #self.sun_color[0]=self.sun_color[0]*1.2
        #self.sun_color[1]=self.sun_color[1]*1.2
        #self.sun_color[2]=self.sun_color[2]*1.2

        p1=self.skyimg.getPixel(x1, 1)
        p2=self.skyimg.getPixel(x2, 1)
        self.sky_color=self.blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 2)
        p2=self.skyimg.getPixel(x2, 2)
        self.cloud_color=self.blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 3)
        p2=self.skyimg.getPixel(x2, 3)
        self.fog_color=self.blendPixels(p1, p2, blend)
        self.fog_color[3]=(abs(sunpos)*0.005+0.001)


        if time<6.0 or time>18.0:
            p=15.0
        else:
            p=sunpos*-180.0
        p=min(60.0, max(-60.0,p))


        self.lights.directionalLight(Vec3(0,p,0), self.sun_color, cfg['glsl-shadow-size'], cfg['glsl-shadow-blur'])

        render.setShaderInput("sunColor",self.sun_color)
        render.setShaderInput("skyColor",self.sky_color)
        render.setShaderInput("cloudColor",self.cloud_color)
        render.setShaderInput("fog", self.fog_color)
