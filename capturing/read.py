from scapy.all import *

a=rdpcap("capture.pcap")
for p in a:
    print(p.summary())
    if p.haslayer(IPv6):
        print("Source IP:", p[IP].src)
        print("Destination IP:", p[IP].dst)
    if p.haslayer(TCP):
        print("Source Port:", p[TCP].sport)
        print("Destination Port:", p[TCP].dport)