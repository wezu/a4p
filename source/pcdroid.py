from panda3d.core import *
from direct.interval.IntervalGlobal import *

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

        # Task
        #taskMgr.add(self.update, 'pc_droid_update')

    #tasks
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
            force=force*50.0
            force = render.getRelativeVector(self.camera_node, force)
            if force.lengthSquared() != 0.0:
                messenger.send('world-player-pod-force',[force])
        return task.cont

    #functions
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

    def lockCamera(self, offset=(0, -6, 1.2)):
        self.camera_node.setPos(render, self.node.getPos(render))
        base.cam.setPos(render, self.node.getPos(render))
        base.cam.setHpr(render, 0,0,0)
        base.cam.setPos(base.cam, offset)
        base.cam.wrtReparentTo(self.camera_gimbal)
        base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)
        taskMgr.add(self.update, 'pc_droid_update')
