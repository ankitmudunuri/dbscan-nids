import pandas as pd
from anom_detection.cluster.dbscan import SeqDBSCAN
from capturing import capture
from processing.processing_thread import ProcessingPool
from queue import Queue
from anom_detection.data_structs.procdata_queue import ProcDataQueue
import time
from threading import Thread
import threading
from anom_detection.preprocessing.data_preprocess import scaling

# Work on changing everything from threading to multiprocessing library to utilize CPU multithreading

if __name__ == "__main__":
    capture_queue = Queue()
    captureflag = threading.Event()
    
    capture_thread = Thread(target=capture.capture_packets, args=(capture_queue, "Ethernet", captureflag,))
    capture_thread.start()

    print("Done capturing")

    ogsize = capture_queue.qsize()
    print("Size of capture queue:", capture_queue.qsize())

    print("Initializing processing data queue")
    procdataqueue = ProcDataQueue()

    print("Initializing DBSCAN")
    seq_dbscan = SeqDBSCAN(eps=0.75, min_samples=3)

    print("Initializing processing pool")
    pool_thread = ProcessingPool(seq_dbscan, capture_queue, procdataqueue, num_threads=12)
    print("Processing")

    while procdataqueue.qsize() < 1000:
        time.sleep(1)
        print(f"{procdataqueue.qsize()}/{ogsize} processed")

    points = []
    while not procdataqueue.empty():
        points.append(procdataqueue.get())

    finaldata = scaling(pd.concat(points)).values.tolist()
    seq_dbscan.process_data(finaldata)

    # Need to add threading to process data from procdata_queue into DBSCAN

    print("Reached 1000 processed points, starting live plotting...")
    seq_dbscan.plot_clusters(k=5, threshold=2.0, animated=True, interval=1000)
    
    print("Plot window closed, stopping processing pool.")
    captureflag.set()
    capture_thread.join()
    pool_thread.kill()

    points = []
    while not procdataqueue.empty():
        points.append(procdataqueue.get())

    if points:
        finaldata = scaling(pd.concat(points)).values.tolist()
        print("Points in total:", len(finaldata))
        seq_dbscan.process_data(finaldata)
        seq_dbscan.plot_clusters(k=5, threshold=2.0, animated=False)
        anoms = seq_dbscan.get_anomalies()
        print("Number of anomalies (noise):", len(anoms))
        suspicious_points = seq_dbscan.compute_anomaly_scores(k=5, threshold=2.0)
        print("Suspicious points based on anomaly scoring:")
        for pt, cid, score in suspicious_points:
            print(f"Point {pt} in cluster {cid} has anomaly score {score:.2f}")
    else:
        print("No points processed.")
