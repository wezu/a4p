from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.stdpy.file import listdir
from collections import deque
import random

class Audio(DirectObject):
    def __init__(self, distance_factor=10.0, doppler_factor=1.0):
        #load all known music files
        log.debug('Audio: loading music')
        self.music={}
        music_dir=listdir(path+'music')
        for music_file in music_dir:
            name=Filename(music_file)
            if  name.getExtension() in ('wav', 'mp3', 'ogg'):
                self.music[name.getBasenameWoExtension()]=loader.loadMusic(path+'music/'+music_file)
        #load all known sfx files
        log.debug('Audio: loading music')
        self.sfx={}
        sfx_dir=listdir(path+'sounds')
        for sfx_file in sfx_dir:
            name=Filename(sfx_file)
            if  name.getExtension() in ('wav', 'mp3', 'ogg'):
                self.sfx[name.getBasenameWoExtension()]=loader.loadSound(base.sfxManagerList[0], path+'sounds/'+sfx_file, True)
        #list of music files to be played
        self.playlist=None
        self.current_track=None
        self.music_volume=0.1
        self.sfx_volume=1.0
        self.shufle=False
        self.seq=None
        self.pause_time=0.0

        base.sfxManagerList[0].audio3dSetDistanceFactor(distance_factor)
        base.sfxManagerList[0].audio3dSetDopplerFactor(doppler_factor)

        log.debug('Audio started')

        #event handling
        self.accept('audio-sfx-2d',self.playSound2D)
        self.accept('audio-sfx-3d',self.playSound3D)

        #task
        taskMgr.add(self.update, 'ui_update')


    def update(self, task):
        if base.sfxManagerList[0].getActive():
            dt=globalClock.getDt()
            pos = base.camera.getPos(render)
            forward = render.getRelativeVector(base.camera, Vec3.forward())
            up = render.getRelativeVector(base.camera, Vec3.up())
            vel = base.camera.getPosDelta(render)/dt
            base.sfxManagerList[0].audio3dSetListenerAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2], forward[0], forward[1], forward[2], up[0], up[1], up[2])
        return task.cont

    def playSound2D(self, sound):
        if sound in self.sfx:
            self.sfx[sound].set3dAttributes(0,0,0, 0,0,0)
            self.sfx[sound].play()
        else:
            log.warning('Audio: unknown sfx: '+sound)

    def playSound3D(self, sound, pos, vel=(0,0,0)):
        if sound in self.sfx:
            self.sfx[sound].set3dAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])
            self.sfx[sound].play()
        else:
            log.warning('Audio: unknown sfx: '+sound)

    def setMusic(self, music):
        music_list=[]
        if isinstance(music, basestring):
            music_list.append(self.music[music])
        else:
            for track in music:
                if track in self.music:
                    music_list.append(self.music[track])
                else:
                    log.warning('Audio: unknown track: '+track)
        self.playlist=deque(music_list)

    def playMusic(self):
        if self.playlist:
            log.debug('Audio: playing music')
            self.current_track=self.playlist.popleft()
            self.playlist.append(self.current_track)
            time=self.current_track.length()
            if time<10.0:
                time=10.1
            if self.shufle:
                #shuffle on a deque can be slow
                #O(n) for deque vs O(1) for list
                #I don't think there should be 1000+ items in the que,
                #so this may be pointless, but you never know...
                shuffle_list=list(self.playlist)
                random.shuffle(shuffle_list)
                self.playlist=deque(shuffle_list)

            #we fade the music in, and then fade it out again
            base.musicManager.setVolume(0.0)
            self.current_track.play()
            self.seq=Sequence(LerpFunc(base.musicManager.setVolume,fromData=0.0,toData=self.music_volume,duration=5.0),
                        Wait(time-10.0),
                        LerpFunc(base.musicManager.setVolume,fromData=self.music_volume,toData=0.0,duration=5.0),
                        Func(self.current_track.stop),
                        Func(self.playMusic))
            self.seq.start()
        else:
            log.warning('Audio: No music on playlist!')

    def resumeMusic(self):
        if self.current_track:
            self.current_track.play()
            self.current_track.setTime(self.pause_time)
            self.seq.resume()

    def pauseMusic(self):
        if self.current_track:
            self.pause_time=self.current_track.getTime()
            self.current_track.stop()
            self.seq.pause()

    def setMusicVolume(self, volume):
        pass

    def setSoundVolume(self, volume):
        pass



