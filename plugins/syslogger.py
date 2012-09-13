# -*- coding: utf-8 -*-
import syslog

class Syslogger:
  config_name = "syslogger"
  plugin_type = "output"

  def output(self, data, layer):
    syslog.openlog("device-tracker")
    for key, value in data.items():
      msg = '{ "@timestamp": "' + value["timestamp"] + '", "@fields": { '
      for name, field in value.items():
        msg = msg + '"' +name + '": "' + field + '", '
      msg = msg + '"layer": "' + layer + '" } }\n'
      syslog.syslog(msg)
