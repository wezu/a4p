from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.stdpy.file import listdir
from collections import deque
import random

class Audio(DirectObject):
    """
    Plays sounds and music.
    """
    def __init__(self):
        #load all known music files
        log.debug('Audio: loading music')

        self.music_manager=base.musicManager
        self.sfx_manager=base.sfxManagerList[0]

        self.music={}
        music_dir=listdir(path+'music')
        for music_file in music_dir:
            name=Filename(music_file)
            if  name.getExtension() in ('wav', 'mp3', 'ogg'):
                self.music[name.getBasenameWoExtension()]=loader.loadMusic(path+'music/'+music_file)
        #load all known sfx files
        log.debug('Audio: loading sounds')
        self.sfx={}
        sfx_dir=listdir(path+'sounds')
        for sfx_file in sfx_dir:
            name=Filename(sfx_file)
            if  name.getExtension() in ('wav', 'mp3', 'ogg'):
                self.sfx[name.getBasenameWoExtension()]=loader.loadSound(self.sfx_manager, path+'sounds/'+sfx_file, True)
        #list of music files to be played
        self.playlist=None
        self.current_track=None
        #set volume
        self.music_volume=cfg['music-volume']
        self.music_manager.setVolume(self.music_volume)
        self.sfx_volume=cfg['sound-volume']
        self.sfx_manager.setVolume(self.sfx_volume)
        #shufle
        self.shufle=False
        #some other stuff...
        self.seq=None
        self.pause_time=0.0
        #list of sounds attached to objects
        self.attached_sounds=[]

        self.sfx_manager.audio3dSetDistanceFactor(cfg['sfx-distance-factor'])
        self.sfx_manager.audio3dSetDopplerFactor(cfg['sfx-doppler-factor'])

        #fp = FilterProperties()
        #fp.addDistort(1.0)
        #self.sfx_manager.configureFilters(fp)

        self.setSpeakerMode(cfg['speakermode'])

        log.debug('Audio started')

        #event handling
        self.accept('audio-sfx',self.playSound)
        self.accept('audio-reset-volume',self.resetVolume)

        #task
        taskMgr.add(self.update, 'audio_update')

    def setSpeakerMode(self, mode):
        if mode == 'raw':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_raw)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_raw)
        elif mode == 'mono':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_mono)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_mono)
        elif mode == 'stereo':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_stereo)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_stereo)
        elif mode == 'quad':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_quad)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_quad)
        elif mode == 'surround':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_surround)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_surround)
        elif mode == '5.1' or mode == 5.1:
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_5point1)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_5point1)
        elif mode == '7.1' or mode == 7.1:
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_7point1)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_7point1)
        elif mode == 'max':
            self.music_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_max)
            self.sfx_manager.setSpeakerSetup(AudioManager.SPEAKERMODE_max)

    def cleanup(self):
        log.debug('Audio: shutdown!')
        self.playlist=None
        self.sfx_manager.stopAllSounds()
        self.music_manager.stopAllSounds()
        self.sfx={}
        self.music={}
        self.sfx_manager.shutdown()
        self.music_manager.shutdown()

    def update(self, task):
        if self.sfx_manager.getActive():
            dt=globalClock.getDt()
            pos = base.cam.getPos(render)
            forward = render.getRelativeVector(base.cam, Vec3.forward())
            up = render.getRelativeVector(base.cam, Vec3.up())
            vel = base.cam.getPosDelta(render)/dt
            self.sfx_manager.audio3dSetListenerAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2], forward[0], forward[1], forward[2], up[0], up[1], up[2])

            #a copy is needed to remove items from the list we are iterating
            for sound_and_node in self.attached_sounds[:]:
                if sound_and_node[0].status() == sound_and_node[0].PLAYING:
                    pos=sound_and_node[1].getPos(render)
                    vel = sound_and_node[1].getPosDelta(render)/dt
                    sound_and_node[0].set3dAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])
                else:
                    self.attached_sounds.remove(sound_and_node)

        return task.cont

    def playSound(self, sound, pos=(0,0,0), vel=(0,0,0)):
        log.debug('Audio: playing: '+str(sound))
        if sound in self.sfx:
            if type(pos).__name__ == 'NodePath':
                self.attached_sounds.append((self.sfx[sound], pos))
                pos=pos.getPos(render)
            self.sfx[sound].set3dAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])
            self.sfx[sound].play()
        else:
            log.warning('Audio: unknown sfx: '+sound)

    def setMusic(self, music):
        music_list=[]
        if isinstance(music, str):
            music_list.append(self.music[music])
        else:
            for track in music:
                if track in self.music:
                    music_list.append(self.music[track])
                else:
                    log.warning('Audio: unknown track: '+track)
        self.playlist=deque(music_list)
        if self.seq:
            try:
                self.seq.finish()
            except:
                log.warning('Audio: something went wrong')

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
            self.music_manager.setVolume(0.0)
            self.current_track.play()
            self.seq=Sequence(LerpFunc(self.music_manager.setVolume,fromData=0.0,toData=self.music_volume,duration=5.0),
                        Wait(time-10.0),
                        LerpFunc(self.music_manager.setVolume,fromData=self.music_volume,toData=0.0,duration=5.0),
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

    def resetVolume(self):
        self.setMusicVolume(cfg['music-volume'])
        self.setSoundVolume(cfg['sound-volume'])


    def setMusicVolume(self, volume):
        self.music_manager.setVolume(volume)
        self.music_volume=volume

    def setSoundVolume(self, volume):
        self.sfx_manager.setVolume(volume)



