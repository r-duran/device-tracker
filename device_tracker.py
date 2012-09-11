# -*- coding: utf-8 -*-
import yaml
import inspect
import time
import sys
from multiprocessing import Process
from plugin_factory import PluginFactory


def runProcess(device_type, output_type, device_layers, device_ip, community):
  print dev + " - " + device_type
  device = factory.getDevicePlugin(device_type, device_ip, community)
  output = factory.getOutputPlugin(output_type)
  for l in device_layers:
    if l.lower() == "l2":
      output.output(device.getL2Data(), l)
    if l.lower() == "l3":
      output.output(device.getL3Data(), l)

if len(sys.argv) < 3:
  print "Config file location needed! use -f 'configfile' commandline argument."
  exit()
elif sys.argv[1] != "-f":
  print "Config file location needed! use -f 'configfile' commandline argument."
  exit()

f = open(sys.argv[2], 'r')
config = yaml.load(f)
print config
f.close()


factory = PluginFactory(config["plugins_dir"])
processes = {}
print time.time()
for dev, options in config["devices"].items():
  processes[dev] = Process(target=runProcess, args=(options["device"], options["output"], options["layers"], dev, options["community"]))
  processes[dev].start()
for dev, process in processes.items():
  process.join()

print time.time()



