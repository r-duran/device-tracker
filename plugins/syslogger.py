# -*- coding: utf-8 -*-
import syslog

class Syslogger:
  config_name = "syslogger"
  plugin_type = "output"

  def output(self, data):
    syslog.openlog("device-tracker")
    for key, value in data.items():
      msg = 'client_mac = "' + key +'" '
      for name, field in value.items():
        msg = msg + name + ' = "' + field + '" '
      syslog.syslog(msg)
