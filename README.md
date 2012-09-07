device-tracker
==============

SNMP based network L2&amp;L3 device tracker with device type and output plugin architecture written in python


Output Plugins
==============
Output plugins need to implement "output(self, data)" method. The "data" is a python dict with the following structure:

{"00:ab:cd:ef:00:11":{"if_index":string, "if_name":string, "if_alias":string, "if_description":string, "if_speed":string,
 "if_mtu":string, "if_pvid":string, "client_mac":string, "vlan":string, "vlan_name":string, "device_name":string,
 "device_system":string, "device_location":string},
 
 "00:ab:cd:ef:00:22":{"if_index":string, "if_name":string, "if_alias":string, "if_description":string, "if_speed":string,
 "if_mtu":string, "if_pvid":string, "client_mac":string, "vlan":string, "vlan_name":string, "device_name":string,
 "device_system":string, "device_location":string},
 ..............
 ..............
 ..............
}

As you see the data dict is indexed with "mac addresses" and each mac address has varius information fields.
