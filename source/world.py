from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject

class World(DirectObject):
    def __init__(self):
        self.world_node = render.attachNewNode('World')
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.objects=[]
        self.player_pod=None
        self.ghost_pods=[]
        self.specjal_objects=[]
        # Task
        taskMgr.add(self.update, 'world_update')
        #events
        self.accept('world-player-pod-force',self.applyPlayerPodForce)
        self.accept('world-move-pod-ghost',self.movePodGhost)

    #task
    def update(self, task):
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 0.001)
        return task.cont

    def onLevelLoad(self, map_name):
        with open(path+'maps/'+map_name+'.json') as f:
            values=json.load(f)
        #the world needs to load/setup:
        # -collidable geometry
        # -the player droid
        # -'specjal' objects


    def movePodGhost(self, pod_id, pos, hpr):
        pass

    def applyPlayerPodForce(self, force):
        pass

    def loadModel(self, model_name):
        model = loader.loadModel(path+'models/'+model_name)
        triMeshData = BulletTriangleMesh()
        for np in model.findAllMatches('**/+GeomNode'):
            geomNode=np.node()
        try:
            for i in range(geomNode.getNumGeoms()):
                geom=geomNode.getGeom(i)
                triMeshData.addGeom(geom)
        except:
             log.warning('World: error loading model: '+model_name)
        shape = BulletTriangleMeshShape(triMeshData, dynamic=False)
        geometry = self.world_node.attachNewNode(BulletRigidBodyNode('model_name'))
        geometry.node().addShape(shape)
        self.world.attachRigidBody(geometry.node())
        self.objects.append(geometry)
        return geometry

    def loadSpecjalObject(self, model_name, pos, hpr, object_type):
        pass
