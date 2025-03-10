from scapy.all import sniff, Packet
import queue

def capture_packets(threadqueue: queue.Queue, interface="Wi-Fi",):
    def push_packet(packet):
        threadqueue.put(packet)

    sniff(iface=interface, prn=push_packet, store=0)

if __name__ == "__main__":
    testqueue = queue.Queue()

    capture_packets(testqueue, interface="Wi-Fi")

