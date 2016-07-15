from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
import random

class PCDroid():
    def __init__(self, ui):
        self.ui=ui
        self.node=render.attachNewNode('pc_droid')
        self.camera_node = render.attachNewNode('camera_node')
        self.camera_gimbal  = self.camera_node.attachNewNode("cameraGimbal")

        self.model=loader.loadModel(path+'models/droid')
        self.model.setShader(Shader.load(Shader.SLGLSL, path+'shaders/droid_v.glsl', path+'shaders/droid_f.glsl'))
        #self.model.setShaderInput("glow_color", Vec3(0.33, 0.894, 1.0)) #no team
        #self.model.setShaderInput("glow_color", Vec3(0.94, 0.0, 0.1)) #red team
        self.model.setShaderInput("glow_color", Vec3(0.33,0.56, 1.0)) #blue team
        self.model.reparentTo(self.node)
        self.model.hide()

        self.rig=loader.loadModel(path+'models/droid_rig')
        self.rig.setShader(Shader.load(Shader.SLGLSL, path+'shaders/droid_v.glsl', path+'shaders/droid_f.glsl'))
        self.rig.setShaderInput("glow_color", Vec3(0.33,0.56, 1.0)) #blue team
        self.rig.reparentTo(self.camera_node)
        self.rig.hide()

        self.movment_vector=Vec3(0, 0, 0)
        self.jump=False
        self.last_jump_time=0.0
        self.last_fire_time=0.0
        # Task
        #taskMgr.add(self.update, 'pc_droid_update')
        #taskMgr.doMethodLater(1.0/30.0,self.networkUpdate, 'pc_droid_net_update')

        #temp hardcode gun
        self.gun=Actor(path+'models/m_pistol',
                        {'fire':path+'models/a_pistol_fire'})
        self.gun.setBlend(frameBlend = True)
        self.gun.setShader(Shader.load(Shader.SLGLSL, path+'shaders/droid_v.glsl', path+'shaders/droid_f.glsl'))
        self.gun.setShaderInput("glow_color", Vec3(0.33,0.56, 1.0)) #blue team
        self.gun.reparentTo(self.camera_gimbal)
        self.gun.setX(1.057)
        self.gun.hide()

        self.gun_flash=loader.loadModel(path+'models/muzzle_flash_pistol')
        self.gun_flash.setShader(Shader.load(Shader.SLGLSL, path+'shaders/flash_v.glsl', path+'shaders/flash_f.glsl'))
        self.gun_flash.reparentTo(self.camera_gimbal)
        self.gun_flash.setX(1.057)
        color_attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOneMinusIncomingColor)
        self.gun_flash.setAttrib(color_attrib)
        self.gun_flash.setBin("fixed", 0)
        self.gun_flash.setDepthTest(True)
        self.gun_flash.setDepthWrite(False)
        self.gun_flash.hide()

    #tasks
    def networkUpdate(self, task):
        #not using networking atm!!!
        messenger.send('world-player-pod-force',[self.movment_vector, self.jump])
        return task.again

    def update(self, task):
        self.camera_node.setPos(render, self.node.getPos(render))
        dt = globalClock.getDt()
        if base.mouseWatcherNode.hasMouse() and self.ui.in_game_menu.is_menu_hidden:

            half_x=base.win.getXSize()//2
            half_y=base.win.getYSize()//2
            delta_x=half_x-base.win.getPointer(0).getX()
            delta_y=half_y-base.win.getPointer(0).getY()

            self.rotate_control(-delta_x*0.01, delta_y*0.01, dt)
            base.win.movePointer(0, half_x, half_y)

            #shoot
            if self.ui.key_map['fire']:
                if globalClock.getRealTime()-self.last_fire_time > 0.3:
                    messenger.send('audio-sfx',['pistol', self.model])
                    self.gun.play('fire')
                    self.last_fire_time=globalClock.getRealTime()
                    self.gun_flash.show()
                    Sequence(Wait(0.1), Func(self.gun_flash.hide)).start()

            force= Vec3(0,0,0)
            if self.ui.key_map['forward']:
                force.setY(1.0)
            if self.ui.key_map['back']:
                force.setY(-1.0)
            if self.ui.key_map['left']:
                force.setX(-1.0)
            if self.ui.key_map['right']:
                force.setX(1.0)
            force.normalize()
            #force=force*50.0
            force = render.getRelativeVector(self.camera_node, force)
            #if force.lengthSquared() != 0.0:
            self.movment_vector=force

            #jump
            if self.ui.key_map['jump']:
                self.jump=True
                if globalClock.getRealTime()-self.last_jump_time > 1.5:
                    messenger.send('audio-sfx',['jump', self.model])
                    self.last_jump_time=globalClock.getRealTime()
            else:
                self.jump=False
                #messenger.send('world-player-pod-force',[force])
        return task.cont

    #functions
    def disable(self):
        self.camera_node.removeNode()
        self.camera_gimbal.removeNode()
        taskMgr.remove('pc_droid_update')
        taskMgr.remove('pc_droid_net_update')

    def setTeam(self, team):
        if team=='red':
            self.model.setShaderInput("glow_color", Vec3(0.94, 0.0, 0.1))
        else:
            self.model.setShaderInput("glow_color", Vec3(0.33,0.56, 1.0))

    def _rotateCamH(self, t):
        self.camera_node.setH(self.camera_node.getH()- t*cfg['mouse-speed'])

    def _rotateCamP(self, t):
        self.camera_gimbal.setP(self.camera_gimbal.getP()+ t*cfg['mouse-speed'])
        if self.camera_gimbal.getP()<-60.0:
            self.camera_gimbal.setP(-60.0)
        if self.camera_gimbal.getP()>30.0:
            self.camera_gimbal.setP(30.0)

    def rotate_control(self, h, p, dt):
        LerpFunc(self._rotateCamH,fromData=0,toData=h, duration=cfg['mouse-lag']+(dt*10.0), blendType='easeInOut').start()
        LerpFunc(self._rotateCamP,fromData=0,toData=p, duration=cfg['mouse-lag']+(dt*10.0), blendType='easeInOut').start()

    def lockCamera(self):
        offset=cfg['camera_offset']
        self.camera_node = render.attachNewNode('camera_node')
        self.camera_gimbal  = self.camera_node.attachNewNode("cameraGimbal")
        self.camera_node.setPos(render, self.node.getPos(render))
        self.rig.reparentTo(self.camera_node)
        self.gun.reparentTo(self.camera_gimbal)
        self.gun.setX(1.057)
        self.gun_flash.reparentTo(self.camera_gimbal)
        self.gun_flash.setX(1.057)
        base.cam.reparentTo(render)
        base.cam.setPos(render, self.node.getPos(render))
        base.cam.setHpr(render, 0,0,0)
        base.cam.setPos(base.cam, offset)
        base.cam.wrtReparentTo(self.camera_gimbal)
        base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)
        taskMgr.add(self.update, 'pc_droid_update')
        taskMgr.doMethodLater(1.0/30.0,self.networkUpdate, 'pc_droid_net_update')
