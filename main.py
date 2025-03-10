import pandas as pd
from anom_detection.cluster.dbscan import SeqDBSCAN

def load_preprocessed_data(csv_file="data/testdata/features_preprocessed.csv"):
    df = pd.read_csv(csv_file)
    return df.values.tolist()

if __name__ == "__main__":
    # Load preprocessed features
    data = load_preprocessed_data()
    
    # Tune eps and min_samples based on your data characteristics
    seq_dbscan = SeqDBSCAN(eps=0.5, min_samples=5)
    seq_dbscan.process_data(data)
    
    seq_dbscan.plot_clusters()
    anoms = seq_dbscan.get_anomalies()
    print(anoms)
    print("Number of anomalies:", len(anoms))
