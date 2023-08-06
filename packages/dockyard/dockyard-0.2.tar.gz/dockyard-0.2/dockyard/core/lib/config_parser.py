from docker_image import *
import copy
import json
        
class ConfigParser(object):
    
    defaults = None

    def __init__(self, defaults):
        self.defaults = defaults

    def imageFromConfig(self, config):
        compiledConfig = copy.copy(self.defaults)
        compiledConfig.update(config)

        dockerImage = DockerImage(**compiledConfig)
        return dockerImage
