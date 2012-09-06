# -*- coding: utf-8 -*-
import subprocess, re

class Generic:
  ifIndexOID = ".1.3.6.1.2.1.2.2.1.1"
  ifDescriptionOID = ".1.3.6.1.2.1.2.2.1.2"
  ifTypeOID = ".1.3.6.1.2.1.2.2.1.3"
  ifMacOID = ".1.3.6.1.2.1.2.2.1.6"
  ifNameOID = ".1.3.6.1.2.1.31.1.1.1.1"
  ifAliasOID = ".1.3.6.1.2.1.31.1.1.1.18"
  ifSpeedOID =  ".1.3.6.1.2.1.2.2.1.5"
  ifMtuOID = ".1.3.6.1.2.1.2.2.1.4"
  ifPvidOID = ".1.3.6.1.2.1.17.7.1.4.5.1.1"

  macVlanOID = ".1.3.6.1.2.1.17.7.1.2.2.1.2"
  portnumToIfIndexOID = ".1.3.6.1.2.1.17.1.4.1.2"
  
  vlanNameOID = ".1.3.6.1.2.1.17.7.1.4.3.1.1"

  deviceNameOID = ".1.3.6.1.2.1.1.5"
  deviceSystemOID = ".1.3.6.1.2.1.1.1"
  deviceLocationOID = ".1.3.6.1.2.1.1.6"
  
  interfaceTable = {}
  vlanTable = {}
  macTable = {}
  
  speeds = {"10000000":"10M", "100000000":"100M", "1000000000":"1G", "10000000000":"10G"}
  
  ip = ""
  community = ""
  name=""
  system=""
  location=""
  
  def __init__(self, device, community):
    self.ip = device
    self.community = community
    self.name = self.getStrippedOIDKeyValueData(self.deviceNameOID)["0"]
    self.system = self.getStrippedOIDKeyValueData(self.deviceSystemOID)["0"]
    self.location = self.getStrippedOIDKeyValueData(self.deviceLocationOID)["0"]
    
    self.buildMacTable()

  def getStrippedOIDKeyValueData(self, oid):
    args = ['snmpbulkwalk', '-v2c', '-OnQ', '-c', self.community, self.ip, oid]
    output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    pattern = oid.replace(".","\.")+"\."+"([^\s]+)\s+=\s+(.*)"
    output = output.replace("\r","")
    result = re.findall(pattern, output)
    data = {}
    for k,v in result:
      v = v.strip("\"").strip("\n")
      if v == "":
        v = "-"
      data[k] = v
    return data

  def getStrippedOIDKeyData(self, oid):
    args = ['snmpbulkwalk', '-v2c', '-OnQ', '-c', self.community, self.ip, oid]
    output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    pattern = oid.replace(".","\.")+"\."+"([^\s]+)\s+="
    data = re.findall(pattern, output)
    return data

  def buildSpeedString(self, speed):
    match = re.findall("10000000{1,3}\\b", speed)
    if match:
      speed = self.speeds[speed]
    else:
      speed = "other"
    return speed

  def buildVlanTable(self):
    self.vlanTable = self.getStrippedOIDKeyValueData(self.vlanNameOID)

  def getMacFromOIDString(self, oid):
    match = re.match("(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})", oid)
    macStr = "-"
    if match:
      macStr=""
      for m in match.groups():
        macStr = macStr + ":" +  hex(int(m)).replace("0x", "")
      macStr = macStr.lstrip(":")
    return macStr

  def buildInterfaceTable(self):
    ifIndexArray = self.getStrippedOIDKeyData(self.ifIndexOID)
    ifNameTable = self.getStrippedOIDKeyValueData(self.ifNameOID)
    ifAliasTable = self.getStrippedOIDKeyValueData(self.ifAliasOID)
    ifSpeedTable = self.getStrippedOIDKeyValueData(self.ifSpeedOID)
    ifMtuTable = self.getStrippedOIDKeyValueData(self.ifMtuOID)
    ifDescriptionTable = self.getStrippedOIDKeyValueData(self.ifDescriptionOID)
    ifPvidTable = self.getStrippedOIDKeyValueData(self.ifPvidOID)
    
    for i in ifIndexArray:
      value = "-"
      if i in ifNameTable:
        value = ifNameTable[i]
      self.interfaceTable[i] = {"name":value}
      value = "-"
      if i in ifAliasTable:
        value = ifAliasTable[i]
      self.interfaceTable[i].update({"alias":value})
      value = "-"
      if i in ifSpeedTable:
        value = self.buildSpeedString(ifSpeedTable[i])
      self.interfaceTable[i].update({"speed":value})
      value = "-"
      if i in ifMtuTable:
        value = ifMtuTable[i]
      self.interfaceTable[i].update({"mtu":value})
      value = "-"
      if i in ifDescriptionTable:
        value = ifDescriptionTable[i]
      self.interfaceTable[i].update({"description":value})
      value = "-"
      if i in ifPvidTable:
        value = ifPvidTable[i]
      self.interfaceTable[i].update({"pvid":value})

  def buildMacTable(self):
    self.buildInterfaceTable()
    self.buildVlanTable()
    for vId, vName in self.vlanTable.items():
      macVlanTable = self.getStrippedOIDKeyValueData(self.macVlanOID+"."+vId)
      for mac,portnum in macVlanTable.items():
        self.macTable[mac] = {"ifindex":portnum, "vlan":vId, "vlan_name":vName}

  def getL2Data(self):
    data = {}
    for mac, fields in self.macTable.items():
      data[self.getMacFromOIDString(mac)] = {"if_index":fields["ifindex"], "if_name":self.interfaceTable[fields["ifindex"]]["name"], \
                                             "if_alias":self.interfaceTable[fields["ifindex"]]["alias"], \
                                             "if_description":self.interfaceTable[fields["ifindex"]]["description"], \
                                             "if_speed":self.interfaceTable[fields["ifindex"]]["speed"], \
                                             "if_mtu":self.interfaceTable[fields["ifindex"]]["mtu"], "if_pvid":self.interfaceTable[fields["ifindex"]]["pvid"], \
                                             "client_mac":self.getMacFromOIDString(mac), "vlan":fields["vlan"], "vlan_name":fields["vlan_name"], \
                                             "device_name":self.name, "device_system":self.system, "device_location":self.location}
    return data




