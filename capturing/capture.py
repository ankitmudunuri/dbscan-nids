from scapy.all import AsyncSniffer, Packet
import queue

def capture_packets(threadqueue: queue.Queue, interface="Wi-Fi",flag = None):
    def push_packet(packet):
            threadqueue.put(packet)

    sniffer = AsyncSniffer(iface=interface, prn=push_packet, store=False)
    sniffer.start()
    while True:
        if flag and flag.is_set():
            sniffer.stop()
            break

if __name__ == "__main__":
    testqueue = queue.Queue()

    capture_packets(testqueue, interface="Wi-Fi")

