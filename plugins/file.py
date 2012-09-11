# -*- coding: utf-8 -*-
import os

class File:
  config_name = "file"
  plugin_type = "output"
  
  output_path = "device-tracker.log"

  def output(self, data, layer):
    try:
      f = open(self.output_path, 'a')
    except IOError:
            print "Can not open file: " + os.path.splitext(file)[0] + "!!!"
            print traceback.format_exc()
    else:
      for key, value in data.items():
        msg = ''
        for name, field in value.items():
          msg = msg + name + '="' + field + '" '
        msg = msg + 'layer="' + layer + '" \n'
        f.write(msg)
      f.close()
