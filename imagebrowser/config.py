#
# IBView Config
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

import os
import json
import platform

import utils

if platform.system() == "Windows":
    HOMEPATH = os.path.normpath(os.environ["USERPROFILE"])
if platform.system() == "Linux":
    HOMEPATH = os.path.normpath(os.path.expanduser('~'))

#------------------------------------------------#
# Config Object
#------------------------------------------------#
class Config(object):
    def __init__(self):

        self.rootPath = os.path.dirname(__file__)
        self.resourcePath = os.path.join(self.rootPath, 'resources')
        self.converterPath = os.path.join(self.rootPath, 'converters')
        self.defaultConfigPath = os.path.join(HOMEPATH, 'ib.conf')
        self.defaultThumbCachePath = os.path.join(HOMEPATH, 'imagebrowsercache')

        # Config
        self.config={
            "application":
                {
                "verbose"               :False,
                "converters"            :[],
                "size_mode"             :2,
                "split_horizontal"      :(200,800),
                "split_vertical"        :(500,500)
                },
            "settings_thumbnail":
                {
                "convert_primary"       :{"current":"qt", "type":"list", "values":[]},
                "convert_secondary"     :{"current":"None", "type":"list", "values":[]},
                "max_size"              :{"current":200, "type":"range", "values":(100,500)},
                "format"                :{"current":"png", "type":"list", "values":["png", "jpg", "tif"]},
                },
            "settings_paths":
                {
                "configpath"            :{"current":self.defaultConfigPath, "type":"filepath", "values":None},
                "cache"                 :{"current":self.defaultThumbCachePath, "type":"path", "values":None}
                },
            "user":
                {
                "presets"               :{}
                }
        }

        # Init Configuration
        if self.loadConfig():
            pass
        else:
            if self.saveConfig():
                pass
            else:
                utils.warn('Could not save config, settings will not be saved!')


    # ----------------- APPLICATION -----------------

    # VERBOSE
    @property
    def verbose(self):
        return self.config['application']['verbose']

    def set_verbose(self, value):
        self.config['application']['verbose']=value

    # CONVERTERS
    @property
    def converters(self):
        self.config['application']['converters']

    def set_converters(self, value):
        self.config['application']['converters']=value
        self.config['settings_thumbnail']['convert_primary']['values']=value
        self.config['settings_thumbnail']['convert_secondary']['values']=['None']+value

    # SIZE MODE
    @property
    def size_mode(self):
        return self.config['application']['size_mode']

    def set_size_mode(self, value):
        self.config['application']['size_mode']=value

    # SPLIT HORIZONTAL
    @property
    def split_horizontal(self):
        return self.config['application']['split_horizontal']

    def set_split_horizontal(self, value):
        self.config['application']['split_horizontal']=value

    # SPLIT VERTICAL
    @property
    def split_vertical(self):
        return self.config['application']['split_vertical']

    def set_split_horizontal(self, value):
        self.config['application']['split_vertical']=value

    # ----------------- WIDGET SETTINGS -----------------

    # MODE
    @property
    def mode(self):
        return self.config['settings_widget']['mode']['current']

    def set_mode(self, value):
        self.config['settings_widget']['mode']['current']=value

    # ----------------- THUMBNAIL SETTINGS -----------------

    # CONVERT PRIMARY
    @property
    def convert_primary(self):
        return self.config['settings_thumbnail']['convert_primary']['current']

    def set_convert_primary(self, value):
        self.config['settings_thumbnail']['convert_primary']['current']=value

    # CONVERT SECONDARY
    @property
    def convert_secondary(self):
        return self.config['settings_thumbnail']['convert_secondary']['current']

    def set_convert_secondary(self, value):
        self.config['settings_thumbnail']['convert_secondary']['current']=value

    # MAX SIZE
    @property
    def max_size(self):
        return self.config['settings_thumbnail']['max_size']['current']

    def set_max_size(self, value):
        self.config['settings_thumbnail']['max_size']['current']=value

    # FORMAT
    @property
    def format(self):
        return self.config['settings_thumbnail']['format']['current']

    def set_format(self, value):
        self.config['settings_thumbnail']['format']['current']=value


    # ----------------- PATH SETTINGS -----------------

    # CONFIG
    @property
    def configpath(self):
        return self.config['settings_paths']['configpath']['current']

    def set_configpath(self, value):
        self.config['settings_paths']['configpath']['current']=value

    # CACHE
    @property
    def cache(self):
        return self.config['settings_paths']['cache']['current']

    def set_cache(self, value):
        self.config['settings_paths']['cache']['current']=value


    # ----------------- USER -----------------

    # PRESET
    @property
    def presets(self):
        return self.config['user']['presets']

    def set_presets(self, value):
        self.config['user']['presets']=value


    # ----------------- Save/Load -----------------
    
    def updateConfig(self, config):
        
        updateConfig = config.copy()
        defaultConfig = self.config

        for category, params in defaultConfig.iteritems():
            if category not in updateConfig:
                updateConfig[category]=params
            
            for pname, pvalue in params.iteritems():
                if pname not in updateConfig[category]:
                    updateConfig[category][pname]=pvalue
                    utils.info('Repaired "%s" config parameter' % pname)
        
        self.config = updateConfig
        self.saveConfig()
    
    #_____________________________________________________________
    def loadConfig(self):
        try:
            with open(self.configpath) as configFile:
                configData = json.load(configFile)

                # update config
                self.updateConfig(configData)
                
            utils.info('Loaded Config')
            return True
        except Exception, e:
            utils.warn(e)
            return False

    #_____________________________________________________________
    def saveConfig(self):
        try:
            with open(self.configpath, 'wb') as configFile:
                json.dump(self.config, configFile)
            
            utils.info('Saved Config')
            return True
        except Exception, e:
            utils.warn(e)
            return False
