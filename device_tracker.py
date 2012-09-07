# -*- coding: utf-8 -*-
import yaml
import inspect
from plugin_factory import PluginFactory

f = open('config.yml', 'r')
config = yaml.load(f)
f.close()

factory = PluginFactory()
dev = factory.getDevicePlugin('cisco', '192.168.11.21', 'as4950')
output = factory.getOutputPlugin('syslogger')
output.output(dev.getL2Data())




