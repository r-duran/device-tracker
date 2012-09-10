# -*- coding: utf-8 -*-
import yaml
import inspect
import time
from multiprocessing import Process
from plugin_factory import PluginFactory


def runProcess(device_type, output_type, device_layers, device_ip, community):
  print dev + " - " + device_type
  device = factory.getDevicePlugin(device_type, device_ip, community)
  output = factory.getOutputPlugin(output_type)
  for l in device_layers:
    if l.lower() == "l2":
      output.output(device.getL2Data())
    if l.lower() == "l3":
      output.output(device.getL3Data())

f = open('config.yml', 'r')
config = yaml.load(f)
print config
f.close()


factory = PluginFactory()
processes = {}
print time.time()
for dev, options in config["devices"].items():
  processes[dev] = Process(target=runProcess, args=(options["device"], options["output"], options["layer"], dev, options["community"]))
  processes[dev].start()
for dev, process in processes.items():
  process.join()

print time.time()



