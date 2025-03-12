import pandas as pd
from anom_detection.cluster.dbscan import SeqDBSCAN
from capturing import capture
from processing.processing_thread import ProcessingPool
from queue import Queue
from anom_detection.data_structs.procdata_queue import ProcDataQueue
import time
from threading import Thread, Event
from anom_detection.preprocessing.data_preprocess import scaling

if __name__ == "__main__":

    capture_queue = Queue()
    captureflag = Event()
    
    capture_thread = Thread(target=capture.capture_packets, args=(capture_queue, "Ethernet", captureflag,))
    capture_thread.start()

    print("Done capturing")
    ogsize = capture_queue.qsize()
    print("Size of capture queue:", capture_queue.qsize())

    print("Initializing processing data queue")
    procdataqueue = ProcDataQueue()

    print("Initializing DBSCAN")
    seq_dbscan = SeqDBSCAN(eps=0.5, min_samples=3)

    print("Initializing processing pool")
    pool_thread = ProcessingPool(seq_dbscan, capture_queue, procdataqueue, num_threads=12)
    print("Processing")

    dbscan_stop_event = Event()

    def dbscan_update():
        while not dbscan_stop_event.is_set():
            new_points = []
            while not procdataqueue.empty():
                new_points.append(procdataqueue.get())
            if len(new_points) >= 100:

                seq_dbscan.process_data(scaling(pd.concat(new_points)).values.tolist())
                new_points = []
            time.sleep(1)

    dbscan_thread = Thread(target=dbscan_update)
    dbscan_thread.start()


    print("Starting live plot (close window to proceed)...")
    seq_dbscan.plot_clusters(k=20, threshold=3.0, animated=True, interval=100)


    print("Plot window closed, stopping processing pool and update thread.")
    dbscan_stop_event.set()
    dbscan_thread.join()


    captureflag.set()
    capture_thread.join()
    pool_thread.kill()

    points = []
    while not procdataqueue.empty():
        points.append(procdataqueue.get())

    if points:
        seq_dbscan.plot_clusters(k=5, threshold=2.75, animated=False)
        anoms = seq_dbscan.get_anomalies()
        print("Number of anomalies (noise):", len(anoms))
        suspicious_points = seq_dbscan.compute_anomaly_scores(k=5, threshold=2.75)
        print("Suspicious points based on anomaly scoring:")
        for pt, cid, score in suspicious_points:
            print(f"Point {pt} in cluster {cid} has anomaly score {score:.2f}")
    else:
        print("No points processed.")
