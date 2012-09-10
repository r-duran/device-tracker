# -*- coding: utf-8 -*-
import syslog

class Syslogger:
  config_name = "syslogger"
  plugin_type = "output"

  def output(self, data, layer):
    syslog.openlog("device-tracker")
    for key, value in data.items():
      msg = ''
      for name, field in value.items():
        msg = msg + name + '="' + field + '" '
      syslog.syslog(msg)
