# arp -a

import ifaddr
from wakeonlan import send_magic_packet


adapters = ifaddr.get_adapters()

for index, adapter in enumerate(adapters):
    if adapter.nice_name ==  "Realtek PCIe GbE Family Controller":
        print ("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            ip_address = "%s" % (ip.ip)
            print(ip_address)
            send_magic_packet('5c.34.00.70.12.7e', '5c.34.00.70.12.4c', '5c.34.00.70.12.77', interface=ip_address)
