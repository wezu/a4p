import __builtin__ as builtins
from direct.showbase.AppRunnerGlobal import appRunner
if appRunner: #run from binary/p3d
    path=appRunner.p3dFilename.getDirname()+'/'
else:  #run from python
    path=''
#some options may need to be set here, but if this file is packed to a
# p3d/exe it might be hard if we don't load the values now
#some important values are set here as default values
from panda3d.core import loadPrcFileData
loadPrcFileData('', 'source-dir source')
loadPrcFileData('', 'game-mode normal')
loadPrcFileData('', 'notify-level-a4p info')
loadPrcFileData('', 'log-file None')
loadPrcFileData('', 'font-default font/DejaVuSans.ttf')
loadPrcFileData('', 'font-special font/visitor2.ttf')
loadPrcFileData('', 'textures-power-2 None')
loadPrcFileData('', 'pause-on-focus-fost True')
loadPrcFileData('', 'ui_color1 0.33 0.894 1.0 1.0')
loadPrcFileData('', 'ui_color2 0.94 0.0 0.1 1.0')
loadPrcFileData('', 'ui_color3 0.33 0.56 1.0 1.0')
loadPrcFileData('', 'window-type none')
#meh, just use one config file - config.txt loaded a bit later
#if the file is lost we still have the basic valuese hardcoded here
#from panda3d.core import loadPrcFile
#loadPrcFile('base_config.prc')
#import the rest
from panda3d.core import *
from direct.showbase import ShowBase
from direct.directnotify.DirectNotify import DirectNotify
import sys
import ast
from datetime import datetime
import traceback

class Configer (object):
    """
    The class will load a config file, it also has a dict-like interface
    """
    def __init__(self, config_file):
        #a temp log is needed, we can't use the 'global' log,
        #we first need to know where/what to log
        #and that info is in the config file we are about to load
        #solution - we store the msg and prit them later when the log system is up
        self.warning=[]
        self.debug=[]
        self.loadConfig(config_file)

    def getItem(self, key):
        if key in self.cfg:
            return self.cfg[key]
        else:
            return self.getValueFromConfigVariable(key)
        return None

    def __getitem__(self, key):
        if key in self.cfg:
            return self.cfg[key]
        else:
            v=self.getValueFromConfigVariable(key)
            self.cfg[key]=v
            return v
        return None

    def __setitem__(self, key, value):
        self.cfg[key]=value

    def __contains__(self, item):
        return item in self.cfg

    def getAllWords(self, var):
        """Returns all values of a config variable as a list
        or the first value if there only is one vaue in the variable
        """
        world_count=var.getNumWords()
        if world_count==1:
            return var.getValue()
        r=[]
        for i in range(world_count):
            r.append(ast.literal_eval(str(var.getWord(i))))
        return tuple(r)

    def getValueFromConfigVariable(self, var_name):
        """Returns the config variable value or values no matter what the
        type of the value is, returns list for multi word variables
        """
        var_type=ConfigVariable(var_name).getValueType()
        #print '(',var_type,')', var_name

        if var_type ==ConfigFlags.VT_list:
            l=[]
            for i in range(ConfigVariableList(var_name).getNumValues()):
                l.append(ConfigVariableList(var_name).getStringValue (i))
            return l
        elif var_type ==ConfigFlags.VT_string:
            return self.getAllWords(ConfigVariableString(var_name))
        elif var_type ==ConfigFlags.VT_filename:
            return self.getAllWords(ConfigVariableFilename(var_name))
        elif var_type ==ConfigFlags.VT_double:
            return self.getAllWords(ConfigVariableDouble(var_name))
        elif var_type ==ConfigFlags.VT_bool:
            return self.getAllWords(ConfigVariableBool(var_name))
        elif var_type ==ConfigFlags.VT_int:
            return self.getAllWords(ConfigVariableInt(var_name))
        elif var_type ==ConfigFlags.VT_enum:
            return self.getAllWords(ConfigVariableString(var_name))
        elif var_type ==ConfigFlags.VT_search_path:
            return ConfigVariableSearchPath(var_name).getValue ()
        elif var_type ==ConfigFlags.VT_int64:
            return self.getAllWords(ConfigVariableDouble(var_name))
        elif var_type ==ConfigFlags.VT_color:
            return ConfigVariableColor(var_name).getValue()
        else:
            #the value is of unkonwn type, probably a custom value
            #load them as strings and then
            #try to turn them into the right type one by one
            variables=self.getAllWords(ConfigVariableString(var_name, ''))
            if len(variables)==0:
                return None
            #is it one word?
            if ConfigVariableString(var_name).getNumWords()==1:
                try:
                   return ast.literal_eval(variables)
                except:
                    #some special strings should be converted to bool
                    if variables in ('false', '#f'):
                        return False
                    if variables in ('true', '#t'):
                        return True
                    return variables
            r=[]
            for var in variables:
                try:
                    r.append(ast.literal_eval(var))
                except:
                    #some special strings should be converted to bool
                    if variables in ('false', '#f'):
                        r.append(False)
                    elif variables in ('true', '#t'):
                        r.append(True)
                    else:
                        r.append(var)
            return tuple(r)
        return None

    def loadConfig(self, config_file_name, load_all=False):
        self.cfg={}
        config_dict={}
        self.debug.append('Loading config from: '+config_file_name)
        try:
            with open(config_file_name,'r') as f:
                for row in f:
                    if not row.startswith('#'):
                        loadPrcFileData('',row)
                        if row.split():
                            var_name=row.split()[0]
                            var_value=self.getValueFromConfigVariable(var_name)
                            config_dict[var_name]=var_value
                            self.debug.append(var_name+' set to '+str(var_value))
        except IOError:
            self.warning.append('Could not load config file: '+config_file_name)

        if load_all:
            self.warning.append('Reading all known config variables!')
            for i in range(ConfigVariableManager.getGlobalPtr().getNumVariables()):
                var_name=ConfigVariableManager.getGlobalPtr().getVariableName(i)
                var_value=self.getValueFromConfigVariable(var_name)
                config_dict[var_name]=var_value
        self.cfg=config_dict

    def saveConfig(self, config_file):
        log.debug('Saving config file to: '+config_file)
        try:
            with open(config_file, 'w') as out_file:
                out_file.write('#A4P config file, edit at your own risk\n')
                for key in sorted(self.cfg):
                    out_file.write(key+' '+self.getCfgValueAsString(key)+'\n')
        except IOError:
            log.warning('Could not save config file: '+config_file)

    def setCfgValueFromString(self, var_name, value):
        if var_name in self.cfg:
            v=self.cfg[var_name]
            if isinstance(v, basestring): #string or unicode
                self.cfg[var_name]=value
            elif hasattr(v, '__iter__'):  #probaly list
                r=[]
                for var in value.split(' '):
                    try:
                        r.append(ast.literal_eval(var))
                    except:
                        #some special strings should be converted to bool
                        if var in ('false', '#f'):
                            r.append(False)
                        elif var in ('true', '#t'):
                            r.append(True)
                        else:
                            r.append(var)
                self.cfg[var_name]=r
            else:
                try:
                   self.cfg[var_name]=(ast.literal_eval(value))
                except:
                    self.cfg[var_name]=value
        else:
                try:
                   self.cfg[var_name]=(ast.literal_eval(value))
                except:
                    self.cfg[var_name]=value

    def getCfgValueAsString(self, var_name):
        if var_name not in self.cfg:
            v=self.getValueFromConfigVariable(var_name)
            self.cfg[var_name]=v
            return self.getCfgValueAsString(var_name)
        v=self.cfg[var_name]
        if isinstance(v, basestring): #string or unicode
            return v
        elif hasattr(v, '__iter__'):  #any type of sequence
            temp_string=''
            for item in v:
                temp_string+=str(item)+' '
            return  temp_string.strip()
        else:
            return str(v)

class Logger:
    """
    Prints messages to the consol and/or file and or gui element
    """
    def __init__(self, gui=None, out_file=None):
        self.notify = DirectNotify().newCategory('a4p')
        self.gui=gui
        self.out_file=None
        if out_file:
            self.out_file=open(path+out_file,'a')
            self.out_file.write('---<Opening file on: '+str(datetime.now())+' >---\n')

        self.debug('Logger is now logging')
        self.debug('Logger gui is '+str(gui))
        self.debug('Logger out_file is '+str(out_file))

    def error(self, msg):
        if self.gui:
            self.gui.showMsg('Error: '+msg)
        if self.out_file:
            self.out_file.write('Error:'+msg+'\n')
        self.notify.warning('Error: '+msg)

    def warning(self, msg):
        self.notify.warning(msg)
        if self.gui:
            self.gui.showMsg('Warning: '+msg)
        if self.out_file:
            self.out_file.write('Warning: '+msg+'\n')

    def info(self, msg):
        self.notify.info(msg)
        if self.gui:
            self.gui.showMsg(msg)
        if self.out_file:
            self.out_file.write(msg)

    def debug(self, msg):
        self.notify.debug(msg)
        if self.gui:
            self.gui.showMsg('Debug: '+msg)
        if self.out_file:
            self.out_file.write('Debug: '+msg+'\n')

    def exception(self, msg):
        if self.gui:
            self.gui.showMsg('Exception: '+msg)
        if self.out_file:
            self.out_file.write('Exception: '+msg+'\n')
        self.notify.error(msg)

    def closeLogFile(self):
        if self.out_file:
            self.out_file.write('---<Closing file on: '+str(datetime.now())+' >---\n')
            self.out_file.close()
        self.out_file=None


class App():
    """
    Program entry point. This class is here to init ShowBase, load config files and launch the game.
    This part of the game can be packed to a p3d/exe/binary while keeping the rest of the game
    as human readable python source files (py), bytecode (pyc), or a compiled extension module (pyd)

    This class creates the fallowing builtins:
    -log (Logger)
    -app (App)
    -cfg (Configer)
    And anything else the ShowBase creates
    """
    def __init__(self):
        #init ShowBase
        base = ShowBase.ShowBase()

        #base.disableMouse()

        #load all the config vars
        builtins.cfg=Configer(path+'config.txt')

        #log/print all messages
        builtins.log=Logger(out_file=cfg['log-file'])

        #print the msg (as needed from the configer
        for msg in cfg.debug:
            log.debug(msg)
        for msg in cfg.warning:
            log.warning(msg)

        #make the path a builtin
        builtins.path=path
        log.debug('Curent working directory is: '+path)

        if cfg['want-pstats']:
            PStatClient.connect()


        #config vars can also be passed as command line arguments
        if len(sys.argv)>1:
            names=sys.argv[1:][::2]
            values=sys.argv[2:][::2]
            for name, value in dict(zip(names, values)).iteritems():
                log.debug('cmd option: '+name+' '+value)
                cfg.setCfgValueFromString(name, value)
                log.debug(name+':'+str(cfg[name]))
        #start the game
        self.startGame(path+cfg['source-dir'])

    def startGame(self, source_dir):
        sys.path.append(source_dir)
        log.debug('Importing Game from: '+source_dir)
        try:
            from game import Game
            self.game=Game()
        except:
            log.error('Can not import the Game module!')
            for error in traceback.format_exc().splitlines()[1:]:
                log.warning(error)
            self.exit()

    def exit(self):
        log.debug('Final message, shuting down.')
        log.closeLogFile()
        base.userExit()

builtins.app=App()
base.run()

