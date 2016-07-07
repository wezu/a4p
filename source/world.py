from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject
import json

class World(DirectObject):
    def __init__(self):
        self.world_node = render.attachNewNode('World')
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.objects=[]
        self.player_pod=None
        self.ghost_pods=[]
        self.specjal_objects=[]
        self.max_v=Vec3(-5.0, -5.0, -5.0)
        self.min_v=Vec3(5.0, 5.0, 5.0)
        self.pc_droid_node=None

        self.last_pc_jump_time=0.0

        # Task
        taskMgr.add(self.update, 'world_update')
        #events
        self.accept('world-player-pod-force',self.applyPlayerPodForce)
        self.accept('world-move-pod-ghost',self.movePodGhost)
        self.accept( 'load-level', self.onLevelLoad)
        self.accept( 'world-link-objects', self.onLinkObject)
        self.accept( 'world-clear-level', self.onClearLevel)
    #task
    def update(self, task):
        if self.pc_droid_node:
            v=self.pc_droid_node.node().getAngularVelocity()
            new_v=v.fmax(self.max_v)
            new_v=new_v.fmin(self.min_v)
            self.pc_droid_node.node().setAngularVelocity(Vec3(new_v))

        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 0.001)
        return task.cont

    def setupPlayerDroid(self):
        shape = BulletSphereShape(1.0)
        self.pc_droid_node = self.world_node.attachNewNode(BulletRigidBodyNode('pc_droid_node'))
        self.pc_droid_node.node().setMass(4.0)
        self.pc_droid_node.node().addShape(shape)
        self.pc_droid_node.node().setActive(True)
        self.pc_droid_node.node().setDeactivationEnabled(False)
        self.pc_droid_node.node().setFriction(1.0)
        self.pc_droid_node.node().setAngularDamping(0.6)
        #self.pc_droid_node.node().setLinearDamping(0.5)
        self.pc_droid_node.setTag('pc_droid_node', '1')
        self.world.attachRigidBody(self.pc_droid_node.node())

    def onClearLevel(self):
        log.debug('World: clearing level')
        for body in self.world.getRigidBodies():
            self.world.remove(body)
        self.world_node.removeNode()
        self.world_node = render.attachNewNode('World')
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.objects=[]
        self.player_pod=None
        self.ghost_pods=[]
        self.specjal_objects=[]
        self.max_v=Vec3(-5.0, -5.0, -5.0)
        self.min_v=Vec3(5.0, 5.0, 5.0)
        self.pc_droid_node=None
        self.last_pc_jump_time=0.0

    def loadLevel(self, task):
        log.debug('World: loading level...')
        with open(path+'maps/'+self.map_name+'.json') as f:
            values=json.load(f)
        #pc droid
        self.setupPlayerDroid()
        #collision geometry
        for id, obj in enumerate(values['objects']):
            mesh=loader.loadModel(path+obj['model'])

            triMeshData = BulletTriangleMesh()
            for np in mesh.findAllMatches("**/+GeomNode"):
                geomNode=np.node()
            try:
                for i in range(geomNode.getNumGeoms()):
                    geom=geomNode.getGeom(i)
                    triMeshData.addGeom(geom)
            except:
                log.warning("Could not load collision mesh: "+path+obj['model'])

            shape = BulletTriangleMeshShape(triMeshData, dynamic=False)
            geometry = self.world_node.attachNewNode(BulletRigidBodyNode('StaticGeometry'))
            geometry.node().addShape(shape)
            geometry.node().setMass(0.0)
            geometry.setPosHpr(tuple(obj['pos']), tuple(obj['hpr']))
            self.world.attachRigidBody(geometry.node())
            geometry.setTag('id_'+str(id), str(id))
        #the world needs to load/setup:
        # -collidable geometry
        # -the player droid
        # -'specjal' objects
        messenger.send('loading-done', ['world'])
        return task.done

    def onLinkObject(self, visible_node, bullet_node_id):
        node=self.world_node.find('**/='+str(bullet_node_id))
        if node:
            node.setPos(render, visible_node.getPos(render))
            node.setHpr(render, visible_node.getHpr(render))
            visible_node.wrtReparentTo(node)
            node.node().setLinearVelocity(Vec3(0,0,0))
        else:
            log.warning('World: '+str(bullet_node_id)+' not found')

    def onLevelLoad(self, map_name):
        self.map_name=map_name
        taskMgr.add(self.loadLevel, 'world_loadLevel_task', taskChain = 'background_chain')

    def movePodGhost(self, pod_id, pos, hpr):
        pass

    def applyPlayerPodForce(self, force, jump):
        self.pc_droid_node.node().applyCentralForce(force*150.0)
        if jump and globalClock.getRealTime()-self.last_pc_jump_time > 1.5:
            self.pc_droid_node.node().applyCentralForce(Vec3(0, 0, 3000.0))
            self.last_pc_jump_time=globalClock.getRealTime()

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
