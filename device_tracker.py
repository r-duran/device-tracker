# -*- coding: utf-8 -*-
import yaml
import inspect
import time
from plugin_factory import PluginFactory

f = open('config.yml', 'r')
config = yaml.load(f)
print config
f.close()

factory = PluginFactory()
print time.time()
for dev, options in config["devices"].items():
  print dev + " - " + options["type"]
  device = factory.getDevicePlugin(options["type"], dev, options["community"])
  output = factory.getOutputPlugin('syslogger')
  output.output(device.getL2Data())
print time.time()



