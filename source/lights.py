# Light Manager for world space lights by wezu (wezu.dev@gmail.com)
# Radius changed to Attenuation to fit p3d lights
# https://github.com/wezu/light_manager
from panda3d.core import *

class LightManager():
    def __init__(self, max_lights=8, ambient=(0.1, 0.1, 0.1)): 
        self.lights=[]
        #shader has a hardcoded limit of 100
        #but use more then 20 with care
        if max_lights>100:
            max_lights=100
        self.max_lights=max_lights
        self.ambientLight(ambient)
        self.update()
        taskMgr.add(self._perFrameUpdate, '_perFrameUpdate')
         
    def _perFrameUpdate(self, task):
        render.setShaderInput("camera_pos", base.cam.getPos(render))
        return task.cont
        
    def ambientLight(self, *args):
        color=[]
        for arg in args:
            color.append(arg)         
        if len(color)==1:                
            render.setShaderInput('ambient', color[0])
        elif len(color)>2:    
            render.setShaderInput('ambient', Vec3(color[0], color[1], color[2]))
        else:
            render.setShaderInput('ambient', Vec3(0.0, 0.0, 0.0))
    
    def directionalLight(self, hpr, color):
        q = Quat()
        q.setHpr(hpr)
        render.setShaderInput('light_vec', q.getForward())
        render.setShaderInput('light_vec_color', color)
            
    def update(self):
        light_pos= PTA_LVecBase4f()
        light_color= PTA_LVecBase4f()
        light_att= PTA_LVecBase4f()
        num_lights=0
        for light in self.lights: 
            if light:
                light_pos.pushBack(UnalignedLVecBase4f(light[0], light[1], light[2], 0.0))
                light_color.pushBack(UnalignedLVecBase4f(light[3], light[4], light[5], light[6]))
                light_att.pushBack(UnalignedLVecBase4f(light[7], light[8], light[9], 0.0))
                #print num_lights, 'light pos: ',(light[0], light[1], light[2], 0.0)
                #print num_lights, 'light color: ',(light[3], light[4], light[5], light[6])
                #print num_lights, 'light att: ',(light[7], light[9], light[9], 0.0)
                num_lights+=1
        for i in range(self.max_lights-num_lights):
            light_pos.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
            light_color.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
            light_att.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))
        render.setShaderInput('light_pos', light_pos)
        render.setShaderInput('light_color', light_color)
        render.setShaderInput('light_att', light_att)
        render.setShaderInput('num_lights', int(num_lights))#this should be an int, damn you outdated ATI driver!              
        
    def addLight(self, pos, color, att, specular=-1.0):
        if specular==-1.0:
            specular=(color[0]+color[1]+color[2])/3.0        
        new_light=[float(pos[0]),float(pos[1]),float(pos[2]),
                   float(color[0]), float(color[1]), float(color[2]),
                   float(specular),
                   float(att[0]), float(att[1]), float(att[2])]
        if len(self.lights)<self.max_lights:
            self.lights.append(new_light)
            self.update()
            return self.lights.index(new_light)
        else:
            index=None
            for light in self.lights:
                if light==None:
                    index=self.lights.index(light)
                    break
            if index:
                self.lights[index]=new_light
                self.update()
                return index
                
    def removeLight(self, id):
        if id <= len(self.lights):
            self.lights[id]=None
            self.update()
        
    def moveLight(self, id, pos):
        if id <= len(self.lights):
            self.lights[id][0]=pos[0]
            self.lights[id][1]=pos[1]
            self.lights[id][2]=pos[2]
            self.update()
                
    def setColor(self, id, color,specular=-1.0):
        if id <= len(self.lights):
            if specular==-1.0:
                specular=(color[0]+color[1]+color[2])/3.0 
            self.lights[id][3]=color[0]
            self.lights[id][4]=color[1]
            self.lights[id][5]=color[2]
            self.lights[id][6]=specular
            self.update()
            
    def setAttenuation(self, id, att):
        if id <= len(self.lights):
            self.lights[id][7]=att[0]
            self.lights[id][8]=att[1]
            self.lights[id][9]=att[2]
            self.update()  
            
    def setLight(self, id, pos, color, att, specular=1.0):
        if id <= len(self.lights):
            self.lights[id][0]=pos[0]
            self.lights[id][1]=pos[1]
            self.lights[id][2]=pos[2]            
            self.lights[id][3]=color[0]
            self.lights[id][4]=color[1]
            self.lights[id][5]=color[2]
            self.lights[id][6]=specular
            self.lights[id][7]=att[0]
            self.lights[id][8]=att[1]
            self.lights[id][9]=att[2]
            self.update() 
