from panda3d.core import *
from direct.interval.IntervalGlobal import *

class PCDroid():
    def __init__(self, ui):
        self.ui=ui
        self.node=render.attachNewNode('pc_droid')
        self.camera_node = self.node.attachNewNode('camera_node')
        self.camera_gimbal  = self.camera_node.attachNewNode("cameraGimbal")

        self.model=loader.loadModel(path+'models/droid')
        self.model.setShader(Shader.load(Shader.SLGLSL, path+'shaders/droid_v.glsl', path+'shaders/droid_f.glsl'))
        self.model.setShaderInput("glow_color", Vec3(0.33, 0.894, 1.0))
        self.model.reparentTo(self.node)
        self.model.hide()

        self.mouse_speed=cfg['mouse-speed']
        self.mouse_lag=cfg['mouse-lag']

        # Task
        #taskMgr.add(self.update, 'pc_droid_update')

    #tasks
    def update(self, task):
        dt = globalClock.getDt()

        half_x=base.win.getXSize()//2
        half_y=base.win.getYSize()//2
        delta_x=half_x-base.win.getPointer(0).getX()
        delta_y=half_y-base.win.getPointer(0).getY()

        self.rotate_control(-delta_x*0.01, delta_y*0.01, dt)
        base.win.movePointer(0, half_x, half_y)
        return task.cont

    #functions
    def _rotateCamH(self, t):
        self.camera_node.setH(self.camera_node.getH()- t*self.mouse_speed)

    def _rotateCamP(self, t):
        self.camera_gimbal.setP(self.camera_gimbal.getP()+ t*self.mouse_speed)
        if self.camera_gimbal.getP()<-60.0:
            self.camera_gimbal.setP(-60.0)
        if self.camera_gimbal.getP()>30.0:
            self.camera_gimbal.setP(30.0)

    def rotate_control(self, h, p, dt):
        LerpFunc(self._rotateCamH,fromData=0,toData=h, duration=self.mouse_lag+(dt*10.0), blendType='easeInOut').start()
        LerpFunc(self._rotateCamP,fromData=0,toData=p, duration=self.mouse_lag+(dt*10.0), blendType='easeInOut').start()

    def lockCamera(self, offset=(0, -6, 1.2)):
        base.cam.setPos(render, self.node.getPos(render))
        base.cam.setHpr(render, 0,0,0)
        base.cam.setPos(base.cam, offset)
        base.cam.wrtReparentTo(self.camera_gimbal)
        base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
        taskMgr.add(self.update, 'pc_droid_update')
