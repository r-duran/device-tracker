# -*- coding: utf-8 -*-
import yaml
import inspect
import time
import sys
from multiprocessing import Process
from plugin_factory import PluginFactory



def runProcess(output_queue, device_type, output_type, device_layers, device_ip, community):
  print dev + " - " + device_type
  device = factory.getDevicePlugin(device_type, device_ip, community)
  for l in device_layers:
    if l.lower() == "l2":
      output_queue[device_ip] = {"data":device.getL2Data(), "type":output_type}
    if l.lower() == "l3":
      output_queue[device_ip] = {"data":device.getL3Data(), "type":output_type}

if __name__ == "__main__":
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
  output_data = {}
  print time.time()
  for dev, options in config["devices"].items():
    processes[dev] = Process(target=runProcess, args=(output_data, options["device"], options["output"], options["layers"], dev, options["community"]))
    processes[dev].start()
  for dev, process in processes.items():
    process.join()
  for k, v in output_data.items():
    output = factory.getOutputPlugin(v["type"])
    output.output(v[data])

  print time.time()



