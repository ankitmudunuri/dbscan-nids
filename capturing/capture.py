from scapy.all import *

packets = sniff(count=25)

wrpcap("capture.pcap", packets)

