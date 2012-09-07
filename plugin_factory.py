# -*- coding: utf-8 -*-
import os
import inspect
import traceback

class PluginFactory:
  device_plugins = {}
  output_plugins = {}
  
  def __init__(self):
    self.registerPlugins()

  def registerPlugins(self):
    for root, dirs, files in  os.walk("plugins"):
      for file in files:
        if (os.path.splitext(file)[1] == ".py") and (not os.path.splitext(file)[0].startswith("__")):
          try:
            module = __import__("plugins." + os.path.splitext(file)[0])
          except:
            print "Can not load plugin module: " + os.path.splitext(file)[0] + "!!!"
            print traceback.format_exc()
          else:
            d = module.__dict__
            d = d[("plugins." + os.path.splitext(file)[0]).split('.')[-1]].__dict__
            for key, value in d.items():
              if inspect.isclass(value) and hasattr(value, "config_name") and hasattr(value, "plugin_type"):
                if value.plugin_type == "device":
                  self.device_plugins[value.config_name] = value
                if value.plugin_type == "output":
                  self.output_plugins[value.config_name] = value

  def getDevicePlugin(self, name, ip, community):
    return self.device_plugins[name](ip, community)

  def getOutputPlugin(self, name):
    return self.output_plugins[name]()



