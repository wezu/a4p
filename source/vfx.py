from direct.particles.ParticleEffect import ParticleEffect
from direct.particles import Particles
from direct.particles import ForceGroup
from panda3d.physics import *
from panda3d.core import *

EXPLICIT = 0
RADIATE = 1
CUSTOM = 2


#quick and dirty way to make a particle effect
def Vfx(preset_name, **kwargs):
    if preset_name == 'menu_ring':
        p=ParticleVfx('menu_ring')
        #set the birth rate and stuff...
        p.setBirth( pool=200,
                    rate=0.1,
                    number=2,
                    spread=1,
                    life=2.5,
                    life_spread=0.5,
                    mass=20.0,
                    mass_spread=5.0)
        #set a ring emmiter
        p.setEmiter(emmiter_type='RingEmitter',
                    radius=kwargs['radius'],
                    angle=0,
                    spread=0)
        #add two forces
        up = LinearSinkForce(Point3(0.0000, 0.0000, 120.0000), LinearDistanceForce.FT_ONE_OVER_R_SQUARED, 2.0, 20.0, True)
        down=LinearSinkForce(Point3(0.0000, 0.0000, -100.0000), LinearDistanceForce.FT_ONE_OVER_R_SQUARED, 2.0, 10.0, True)
        p.addForce(up, 'up')
        p.addForce(down, 'down')
        p.setForce('up', 0)
        #set blending
        p.setAdditiveBlend()
        #load shader and texture
        inputs={'tex':loader.loadTexture(path+'particle/tex0.png'),
                'radius': 30.0}
        p.setShader(path+'shaders/particle_v.glsl',path+'shaders/particle_f.glsl', inputs)
        p.setHpr(0, 90, 0)
        p.setColor(kwargs['color'])
        p.start(parent=kwargs['parent'])
        return p

class ParticleVfx():
    """
    Wrapper class for ParticleEffect
    """
    def __init__(self, name='particles-1'):
        self.node = ParticleEffect()
        self.p0 = Particles.Particles(name)
        self.p0.setFactory('PointParticleFactory')
        self.p0.setRenderer('PointParticleRenderer')
        self.p0.setLocalVelocityFlag(1)
        self.p0.setSystemGrowsOlderFlag(0)
        self.f0 = ForceGroup.ForceGroup('default')
        self.birth_set=False
        self.emitter_set=False
        self.force={}

    def setHpr(self, node=render, hpr=Vec3(0,0,0), r=None):
        if not r is None:
            hpr=Vec3(node, hpr, r)
            node=render
        elif type(node).__name__ != 'NodePath':
            hpr=node
            node=render
        self.node.setHpr(node, hpr)

    def setPos(self, node=render, pos=Point3(0,0,0), z=None):
        if not z is None:
            pos=Vec3(node, pos, z)
            node=render
        elif type(node).__name__ != 'NodePath':
            pos=node
            node=render
        self.node.setPos(node, pos)

    def hide(self):
        #self.node.disable() #  ParticleEffect.disable() would detach the node and the info on pos/hpr will be lost
        for f in self.node.forceGroupDict.values():
            f.disable()
        for p in self.node.particlesDict.values():
            p.setRenderParent(p.node)
            p.disable()

    def show(self):
        self.node.enable()

    def setBirth(self, pool=300, rate=0.1, number=10, spread=5, life=1.0, life_spread=0.1, mass=10.0, mass_spread=5.0):
        if mass_spread >= mass:
            mass_spread = mass*0.95
        self.p0.setPoolSize(pool)
        self.p0.setBirthRate(rate)
        self.p0.setLitterSize(number)
        self.p0.setLitterSpread(spread)
        self.p0.factory.setLifespanBase(life)
        self.p0.factory.setLifespanSpread(life_spread)
        self.p0.factory.setMassBase(mass)
        self.p0.factory.setMassSpread(mass_spread)
        self.birth_set=True

    def setEmiter(self, emmiter_type='PointEmitter', force=Vec3(0,0,0), emmision_type=EXPLICIT, **kwargs):
        self.p0.setEmitter(emmiter_type)
        self.p0.emitter.setEmissionType(emmision_type)
        self.p0.emitter.setOffsetForce(force)
        self.p0.emitter.setExplicitLaunchVector(Vec3(0,0,0))
        self.p0.emitter.setRadiateOrigin(Point3(0,0,0))
        self.emitter_set=True

        if emmiter_type == 'BoxEmitter':
            self.p0.emitter.setMaxBound(kwargs['max_bound'])
            self.p0.emitter.setMinBound(kwargs['min_bound'])
        elif emmiter_type == 'DiscEmitter':
            self.p0.emitter.setRadius(kwargs['radius'])
            self.p0.emitter.setInnerAngle(kwargs['inner_angle'])
            self.p0.emitter.setInnerMagnitude(kwargs['inner_mag'])
            self.p0.emitter.setOuterAngle(kwargs['outer_angle'])
            self.p0.emitter.setOuterMagnitude(kwargs['outer_mag'])
        elif emmiter_type == 'LineEmitter':
            self.p0.emitter.setEndpoint1(kwargs['endpoint1'])
            self.p0.emitter.setEndpoint2(kwargs['endpoint2'])
        #elif emmiter_type == 'PointEmitter':
        #    pass #no options here
        elif emmiter_type == 'RectangleEmitter':
            self.p0.emitter.setMaxBound(kwargs['max_bound'])
            self.p0.emitter.setMinBound(kwargs['min_bound'])
        elif emmiter_type == 'RingEmitter':
            self.p0.emitter.setAngle(kwargs['angle'])
            self.p0.emitter.setRadius(kwargs['radius'])
            self.p0.emitter.setRadiusSpread(kwargs['spread'])
        elif emmiter_type == 'SphereSurfaceEmitter':
            self.p0.emitter.setRadius(kwargs['radius'])
        elif emmiter_type == 'SphereVolumeEmitter':
            self.p0.emitter.setRadius(kwargs['radius'])
        elif emmiter_type == 'TangentRingEmitter':
            self.p0.emitter.setRadius(kwargs['radius'])
            self.p0.emitter.setRadiusSpread(kwargs['spread'])

        self.node.addParticles(self.p0)

    def setColor(self, color):
        self.p0.renderer.setStartColor(color)
        self.p0.renderer.setEndColor(color)

    def setAdditiveBlend(self):
        color_attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
        for geom in self.node.findAllMatches('**/+GeomNode'):
            geom.setAttrib(color_attrib)
            geom.setDepthWrite(False)
            geom.setDepthTest(False)

    def setShader(self, v_shader, f_shader, inputs={}):
        shader_attrib = ShaderAttrib.make(Shader.load(Shader.SLGLSL, v_shader,f_shader))
        shader_attrib = shader_attrib.setFlag(ShaderAttrib.F_shader_point_size, True)

        for geom in self.node.findAllMatches('**/+GeomNode'):
            geom.setAttrib(shader_attrib)
            for name, value in inputs.items():
                geom.setShaderInput(name, value)

    def addForce(self, force, name):
        force.setVectorMasks(1, 1, 1)
        force.setActive(1)
        self.f0.addForce(force)
        self.force[name]=force

    def setForce(self, name, active=1):
        if name in self.force:
            self.force[name].setVectorMasks(active, active, active)
            #self.force[name].setActive(active) #somehow this fails (?)

    def start(self, parent=render, renderParent = render):
        if not self.emitter_set:
            self.setEmiter()
        if not self.birth_set:
            self.setBirth()
        self.node.addForceGroup(self.f0)
        self.node.start(parent=parent, renderParent = renderParent)

