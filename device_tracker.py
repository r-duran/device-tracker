# -*- coding: utf-8 -*-
import pprint

from plugins.generic import Generic

pp = pprint.PrettyPrinter(depth=6)

dev = Generic('192.168.10.98', 'as4950')
print dev.name
print dev.system
print dev.location
data = dev.buildInterfaceTable()

pp.pprint(data)
