import json
import logging
import inject
from mfcloud.config import YamlConfig, ConfigParseError
import os
from twisted.internet import defer, reactor
import txredisapi


class Application(object):

    def __init__(self, config, name=None):
        super(Application, self).__init__()

        self.config = config
        self.name = name

    def load(self):

        if 'path' in self.config:
            yaml_config = YamlConfig(file=os.path.join(self.config['path'], 'mfcloud.yml'), app_name=self.name)
        elif 'source' in self.config:
            yaml_config = YamlConfig(source=self.config['source'], app_name=self.name)
        else:
            raise ConfigParseError('Can not load config.')

        yaml_config.load()

        d = defer.DeferredList([service.inspect() for service in yaml_config.get_services().values()])
        d.addCallback(lambda *result: yaml_config)
        return d


class AppDoesNotExist(Exception):
    pass


class ApplicationController(object):

    redis = inject.attr(txredisapi.Connection)

    def create(self, name, config, skip_validation=False):

        # validate first
        if not skip_validation:
            Application(config).load()

        d = self.redis.hset('mfcloud-apps', name, json.dumps(config))
        d.addCallback(lambda r: Application(config, name=name))

        return d

    def remove(self, name):
        return self.redis.hdel('mfcloud-apps', name)

    def get(self, name):

        d = self.redis.hget('mfcloud-apps', name)

        def ready(config):
            if not config:
                raise AppDoesNotExist('Application with name "%s" do not exist' % name)
            else:
                app = Application(json.loads(config), name=name)
                return app

        d.addCallback(ready)

        return d

    def list(self):
        d = self.redis.hgetall('mfcloud-apps')

        def ready(config):
            return dict([(name, Application(json.loads(config), name=name)) for name, config in config.items()])
        d.addCallback(ready)

        return d