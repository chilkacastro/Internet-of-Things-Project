"""PyBluez simple example inquiry.py
Performs a simple device inquiry followed by a remote name request of each
discovered device
Author: Albert Huang <albert@csail.mit.edu>
$Id: inquiry.py 401 2006-05-05 19:07:48Z albert $
"""

import bluetooth

print("Performing inquiry...")

nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True,
                                            flush_cache=True, lookup_class=False)

print("Found {} devices".format(len(nearby_devices)))