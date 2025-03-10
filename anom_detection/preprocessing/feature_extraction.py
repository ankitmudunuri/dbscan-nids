from scapy.all import rdpcap
import pandas as pd

def extract_features(packet):
    features = {}
    features["packet_length"] = len(packet)
    
    if packet.haslayer("IP"):
        ip_layer = packet["IP"]
        features["ttl"] = ip_layer.ttl
        features["protocol"] = ip_layer.proto
    else:
        features["ttl"] = 0
        features["protocol"] = 0
        
    if packet.haslayer("TCP"):
        tcp_layer = packet["TCP"]
        features["src_port"] = tcp_layer.sport
        features["dst_port"] = tcp_layer.dport
    elif packet.haslayer("UDP"):
        udp_layer = packet["UDP"]
        features["src_port"] = udp_layer.sport
        features["dst_port"] = udp_layer.dport
    else:
        features["src_port"] = 0
        features["dst_port"] = 0
        
    return features

def process_pcap(pcap_file, output_csv="data/testdata/features.csv"):
    packets = rdpcap(pcap_file)
    feature_list = []
    for pkt in packets:
        feat = extract_features(pkt)
        feature_list.append(feat)
    df = pd.DataFrame(feature_list)
    df.to_csv(output_csv, index=False)
    print(f"Extracted features saved to {output_csv}")

if __name__ == "__main__":
    pcap_file = "data/testdata/capture.pcap"
    process_pcap(pcap_file)
