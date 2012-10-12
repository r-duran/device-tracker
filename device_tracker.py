# -*- coding: utf-8 -*-
import yaml
import inspect
import time
import sys, traceback
from multiprocessing import Process, Queue
from plugin_factory import PluginFactory



def runProcess(q, device_type, output_type, device_layers, device_ip, community):
  device = factory.getDevicePlugin(device_type, device_ip, community)
  for l in device_layers:
    if l.lower() == "l2":
      try:
        data = device.getL2Data()
        if data:
          q.put({"data":data, "type":output_type, "device":device_ip})
      except:
        print "Cant put result to queue"
        print traceback.format_exc()
    if l.lower() == "l3":
      try:
        data = device.getL3Data()
        if data:
          q.put({"data":data, "type":output_type, "device":device_ip})
      except:
        print "Cant put result to queue"
        print traceback.format_exc()
  q.put({"status":"DONE", "device":device_ip})

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "Config file location needed! use -f 'configfile' commandline argument."
    exit()
  elif sys.argv[1] != "-f":
    print "Config file location needed! use -f 'configfile' commandline argument."
    exit()

  f = open(sys.argv[2], 'r')
  config = yaml.load(f)
  f.close()


  factory = PluginFactory(config["plugins_dir"])
  processes = {}
  output_data = Queue()
  print time.time()
  for dev, options in config["devices"].items():
    processes[dev] = Process(target=runProcess, args=(output_data, options["device"], options["output"], options["layers"], dev, options["community"]))
    processes[dev].start()
  while True:
    try:
      if len(processes) == 0:
        break
      data = output_data.get()
      if "status" in data:
        processes[data["device"]].join()
        del processes[data["device"]]
      else:
        output = factory.getOutputPlugin(data["type"])
        output.output(data["data"])
    except:
      print "Queue read error"
      print traceback.format_exc()
      break

  print time.time()

