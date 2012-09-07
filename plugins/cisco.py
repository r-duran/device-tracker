# -*- coding: utf-8 -*-
from generic import Generic
class Cisco(Generic):
  config_name = "cisco"
  plugin_type = "device"

  vlanNameOID = ".1.3.6.1.4.1.9.9.46.1.3.1.1.4.1"
  ifPvidOID = ".1.3.6.1.4.1.9.9.68.1.2.2.1.2"
  macVlanOID = ".1.3.6.1.2.1.17.4.3.1.2"

  def buildMacTable(self):
    self.buildInterfaceTable()
    self.buildVlanTable()
    for vId, vName in self.vlanTable.items():
      macVlanTable = self.getStrippedOIDKeyValueData(self.macVlanOID, self.community+"@"+vId)
      portNumToIfIndexTable = self.getStrippedOIDKeyValueData(self.portnumToIfIndexOID, self.community+"@"+vId)
      for mac,portnum in macVlanTable.items():
        self.macTable[mac] = {"ifindex":portNumToIfIndexTable[portnum], "ifnum":portnum, "vlan":vId, "vlan_name":vName}


