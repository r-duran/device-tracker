# -*- coding: utf-8 -*-
import subprocess, re, datetime

class Generic:

  config_name = "generic"
  plugin_type = "device"

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
  
  ipV4V6ArpOID = ".1.3.6.1.2.1.4.35.1.4"
  ipV4ArpOID = ".1.3.6.1.2.1.4.22.1.2"
  ipV6ArpOID = ".1.3.6.1.2.1.55.1.12.1.2"
  
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
    self.name = self.getStrippedOIDKeyValueData(self.deviceNameOID, self.community)["0"]
    self.system = self.getStrippedOIDKeyValueData(self.deviceSystemOID, self.community)["0"]
    self.location = self.getStrippedOIDKeyValueData(self.deviceLocationOID, self.community)["0"]
    
    self.buildMacTable()

  def getStrippedOIDKeyValueData(self, oid, community):
    args = ['snmpbulkwalk', '-v2c', '-OnQ', '-c', community, self.ip, oid]
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

  def getStrippedOIDKeyData(self, oid, community):
    args = ['snmpbulkwalk', '-v2c', '-OnQ', '-c', community, self.ip, oid]
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
    self.vlanTable = self.getStrippedOIDKeyValueData(self.vlanNameOID, self.community)

  def getMacFromOIDString(self, oid):
    match = re.match("(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})", oid)
    macStr = "-"
    if match:
      macStr=""
      for m in match.groups():
        digit = hex(int(m)).replace("0x", "")
        if len(digit) == 1:
          digit = "0" + digit
        macStr = macStr + ":" + digit 
      macStr = macStr.lstrip(":")
    return macStr

  def getMacFromString(self, macStr):
    macStr = macStr.strip().lower().replace(" ", ":")
    match = re.findall("([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2})", macStr)
    if not match:
      return "-"
    mac = []
    for m in match[0]:
      if len(m) == 1:
        m = "0" + m
      mac.append(m)
    return ":".join(mac)

  def getIpV4FromOIDString(self, oid):
    match = re.findall("(\d{1,3})", oid)
    ip = "-"
    if len(match) > 4:
      ip = ".".join(match[-4:])
    return ip

  def getIpV6FromOIDString(self, oid):
    match = re.findall("(\d{1,3})", oid)
    if len(match) < 17:
      return "-"
    match = match[-16:]
    ip = ""
    word = ""
    c = 0
    for m in match:
      digit = hex(int(m)).replace("0x", "")
      if len(digit) == 1:
        digit = "0" + digit
      if (c % 2 == 0):
        if digit == "00":
          word = ""
        elif digit[0] == "0":
          word = digit[1]
        else:
          word = digit
      if (c != 15) and (c % 2 == 1):
        if word == "" and digit[0] == "0":
          digit = digit[1]
        ip = ip + word + digit + ":"
      if (c == 15) and (c % 2 == 1):
        if word == "" and digit[0] == "0":
          digit = digit[1]
        ip = ip + word + digit
      c = c + 1
    return ip

  def buildInterfaceTable(self):
    ifIndexArray = self.getStrippedOIDKeyData(self.ifIndexOID, self.community)
    ifNameTable = self.getStrippedOIDKeyValueData(self.ifNameOID, self.community)
    ifAliasTable = self.getStrippedOIDKeyValueData(self.ifAliasOID, self.community)
    ifSpeedTable = self.getStrippedOIDKeyValueData(self.ifSpeedOID, self.community)
    ifMtuTable = self.getStrippedOIDKeyValueData(self.ifMtuOID, self.community)
    ifDescriptionTable = self.getStrippedOIDKeyValueData(self.ifDescriptionOID, self.community)
    ifPvidTable = self.getStrippedOIDKeyValueData(self.ifPvidOID, self.community)
    
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
      macVlanTable = self.getStrippedOIDKeyValueData(self.macVlanOID+"."+vId, self.community)
      portNumToIfIndexTable = self.getStrippedOIDKeyValueData(self.portnumToIfIndexOID, self.community)
      for mac,portnum in macVlanTable.items():
        try:
          self.macTable[mac] = {"ifindex":portNumToIfIndexTable[portnum], "ifnum":portnum, "vlan":vId, "vlanname":vName}
        except KeyError:
          continue

  def getL2Data(self):
    data = {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for mac, fields in self.macTable.items():
      data[self.getMacFromOIDString(mac)] = {"ifindex":fields["ifindex"], "ifnum":fields["ifnum"], "ifname":self.interfaceTable[fields["ifindex"]]["name"], \
                                             "ifalias":self.interfaceTable[fields["ifindex"]]["alias"], \
                                             "ifdescription":self.interfaceTable[fields["ifindex"]]["description"], \
                                             "ifspeed":self.interfaceTable[fields["ifindex"]]["speed"], "timestamp":timestamp, \
                                             "ifmtu":self.interfaceTable[fields["ifindex"]]["mtu"], "ifpvid":self.interfaceTable[fields["ifindex"]]["pvid"], \
                                             "clientmac":self.getMacFromOIDString(mac), "vlan":fields["vlan"], "vlanname":fields["vlanname"], \
                                             "devicename":self.name, "devicesystem":self.system, "devicelocation":self.location, "deviceip":self.ip}
    return data

  def getL3Data(self):
    data = {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ipv4Table = self.getStrippedOIDKeyValueData(self.ipV4ArpOID, self.community)
    for ip, mac in ipv4Table.items():
       ip = self.getIpV4FromOIDString(ip)
       mac = self.getMacFromString(mac)
       if (ip != "-") and (mac != "-") and (mac != "00:00:00:00:00:00"):
        data[ip] = {"clientip":ip, "clientmac":mac, "devicename":self.name, "devicesystem":self.system, "devicelocation":self.location, "deviceip":self.ip, "timestamp":timestamp}

    ipv6Table = self.getStrippedOIDKeyValueData(self.ipV6ArpOID, self.community)
    if len(ipv6Table) > 0:
      for ip, mac in ipv6Table.items():
        ip = self.getIpV6FromOIDString(ip)
        mac = self.getMacFromString(mac)
        if (ip != "-") and (mac != "-") and (mac != "00:00:00:00:00:00"):
          data[ip] = {"clientip":ip, "clientmac":mac, "devicename":self.name, "devicesystem":self.system, "devicelocation":self.location, "deviceip":self.ip, "timestamp":timestamp}
    else:
      ipv6Table = self.getStrippedOIDKeyValueData(self.ipV4V6ArpOID, self.community)
      for ip, mac in ipv6Table.items():
        ip = self.getIpV6FromOIDString(ip)
        mac = self.getMacFromString(mac)
        if (ip != "-") and (mac != "-") and (mac != "00:00:00:00:00:00"):
          data[ip] = {"clientip":ip, "clientmac":mac, "devicename":self.name, "devicesystem":self.system, "devicelocation":self.location, "deviceip":self.ip, "timestamp":timestamp}
    return data




